# -*- coding: utf-8 -*-
import logging
import types

from sqlalchemy.ext.declarative import DeclarativeMeta
import sqlalchemy as sa
from zope.interface import Interface, implementedBy, providedBy
from zope.interface.adapter import AdapterRegistry
from zope.interface.interfaces import IInterface

LOG = logging.getLogger(__name__)

_marker = object()


class IServiceClassifier(Interface):
    """ A marker interface to differentiate services from other objects
    in a shared registry."""


def includeme(config):
    config.add_request_method(find_model)
    config.add_request_method(
        lambda _: AdapterRegistry(),
        'model_cache',
        reify=True,
    )

    config.add_directive('register_model', register_model)
    config.add_directive('register_model_factory', register_model_factory)


class ServiceInfo(object):
    def __init__(self, factory, context_iface):
        self.factory = factory
        self.context_iface = context_iface


def register_model(
        config,
        models,
        iface=Interface,
        context=Interface,
):
    models = config.maybe_dotted(models)
    models_factory = add_models(models)

    for model_class in models_factory:
        LOG.debug(model_class.__tablename__)
        config.register_model_factory(
            model_class,
            iface,
            context=context,
            name=model_class.__tablename__
        )


# for single model
def register_model_factory(
        config,
        model_factory,
        iface=Interface,
        context=Interface,
        name='',
):
    model_factory = config.maybe_dotted(model_factory)
    iface = config.maybe_dotted(iface)
    context = config.maybe_dotted(context)

    if not IInterface.providedBy(context):
        context_iface = implementedBy(context)
    else:
        context_iface = context

    info = ServiceInfo(model_factory, context_iface)

    def register():
        adapters = config.registry.adapters
        adapters.register(
            (IServiceClassifier, context_iface),
            iface,
            name,
            info,
        )

    discriminator = ('model factories', (iface, context, name))
    type_name = type(model_factory).__name__

    intr = config.introspectable(
        category_name='baka_tenshi_services',
        discriminator=discriminator,
        title=str((iface.__name__, context.__name__, name)),
        type_name=type_name,
    )
    intr['name'] = name
    intr['type'] = iface
    intr['context'] = context
    config.action(discriminator, register, introspectables=(intr,))


def find_model(request, name, iface=Interface, context=_marker):
    if context is _marker:
        context = getattr(request, 'context', None)

    context_iface = providedBy(context)
    svc_types = (IServiceClassifier, context_iface)

    cache = request.model_cache
    svc = cache.lookup(svc_types, iface, name=name, default=None)
    if svc is None:
        adapters = request.registry.adapters
        info = adapters.lookup(svc_types, iface, name=name)
        if info is None:
            raise ValueError('could not find registered service')
        svc = info.factory
        cache.register(
            (IServiceClassifier, info.context_iface),
            iface,
            name,
            svc,
        )
    return svc


def add_models(models):
    # Build a list of declarative models to add as collections.
    if isinstance(models, types.ModuleType):
        model_list = []
        for attr in models.__dict__.values():
            if isinstance(attr, DeclarativeMeta):
                try:
                    keycols = sa.inspect(attr).primary_key
                except sa.exc.NoInspectionAvailable:
                    # Trying to inspect the declarative_base() raises this
                    # exception. We don't want to add it to the API.
                    continue
                model_list.append(attr)
    else:
        model_list = list(models)

    return model_list
