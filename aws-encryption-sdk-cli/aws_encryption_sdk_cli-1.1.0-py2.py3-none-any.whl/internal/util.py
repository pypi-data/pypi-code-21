""""""
import importlib
import logging

import aws_encryption_sdk

from .identifiers import KNOWN_MASTER_KEY_PROVIDERS

_LOGGER = logging.getLogger(__name__)


def _class_loader(namespace_string):
    """Load a class from a namespace string.

    :param str namespace_string: Full namespace path of desired class
    :returns: Class object
    :rtype: type
    """
    module_name, class_name = namespace_string.rsplit('.', 1)
    try:
        module = importlib.import_module(module_name)
    except TypeError:
        raise ImportError("No module named '{}'".format(module_name))
    try:
        loaded_callable = getattr(module, class_name)
        if not callable(loaded_callable):
            raise ImportError("Target callable '{target}' is not callable".format(namespace_string))
    except AttributeError:
        raise ImportError("Callable '{target}' not found in module '{module}'".format(
            target=class_name,
            module=module
        ))


def _build_master_key_provider_old(provider, *keys):
    """Given a provider identifier and one or more key IDs, builds a Master Key Provider
    instance with all key IDs loaded.

    :param str provider: Known provider ID or namespace path to MasterKeyProvider class
    :param *keys: Key IDs to add to MasterKeyProvider instance
    :returns: Loaded and populated MasterKeyProvider instance
    :rtype: aws_encryption_sdk.key_providers.base.MasterKeyProvider
    """
    _LOGGER.debug('Loading provider: %s', provider)
    provider_class_path = KNOWN_MASTER_KEY_PROVIDERS.get(provider, provider)
    provider_class = _class_loader(provider_class_path)
    key_provider = provider_class()
    for key in keys:
        key_provider.add_master_key(key)
    return key_provider


def _build_master_key_provider(provider, **kwargs):
    """"""
    _LOGGER.debug('Loading provider: %s', provider)
    provider_class_path = KNOWN_MASTER_KEY_PROVIDERS.get(provider)
    provider_class = _class_loader(provider_class_path)
    keys = kwargs.pop('key')
    key_provider = provider_class(**kwargs)
    for key in keys:
        key_provider.add_master_key(key)
    return key_provider


def _assemble_master_key_providers(primary_provider, *providers):
    """Given one or more MasterKeyProvider instance, loads first MasterKeyProvider instance
    with all remaining MasterKeyProvider instances.

    :param primary_provider: MasterKeyProvider to use as the primary (ie: generates the Data Key)
    :type primary_provider: aws_encryption_sdk.key_providers.base.MasterKeyProvider
    :param *providers: MasterKeyProviders to add to primary_provider
    :returns: primary_provider with all other providers added to it
    :rtype: aws_encryption_sdk.key_providers.base.MasterKeyProvider
    """
    for provider in providers:
        primary_provider.add_master_key_provider(provider)
    return primary_provider


def _parse_master_key_providers_from_args(*key_providers_info):
    """Parses the input key info from argparse and loads all key providers and key IDs.

    :param *key_providers_info: One or more dict containing key provider configuration (see _build_master_key_provider)
    :returns: MasterKeyProvider instance containing all referenced providers and keys
    :rtype: aws_encryption_sdk.key_providers.base.MasterKeyProvider
    """
    key_providers = []
    for provider_info in key_providers_info:
        key_providers.append(_build_master_key_provider(**provider_info))
    return _assemble_master_key_providers(*key_providers)


def build_crypto_materials_manager_from_args(key_providers_config, caching_config):
    """Builds a cryptographic materials manager from the provided arguments.

    :param list key_providers_config: List of one or more dicts containing key provider configuration
    :rtype: aws_encryption_sdk.materials_managers.base.CryptoMaterialsManager
    """
    caching_config = caching_config.copy()
    key_provider = _parse_master_key_providers_from_args(*key_providers_config)
    cmm = aws_encryption_sdk.DefaultCryptoMaterialsManager(key_provider)

    if caching_config is None:
        return cmm

    cache = aws_encryption_sdk.LocalCryptoMaterialsCache(capacity=caching_config.pop('capacity'))
    return aws_encryption_sdk.CachingCryptoMaterialsManager(
        materials_manager=cmm,
        cache=cache,
        **caching_config
    )
