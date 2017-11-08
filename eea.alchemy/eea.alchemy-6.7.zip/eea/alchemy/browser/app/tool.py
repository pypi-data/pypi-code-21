""" Alchemy controllers
"""
import logging
import transaction
from zope.component import queryUtility, queryAdapter
from zope.schema.interfaces import IVocabularyFactory

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

from eea.alchemy.interfaces import IDiscoverAdapter

logger = logging.getLogger('eea.alchemy')

class Alchemy(BrowserView):
    """ Main Controller

        >>> self.loginAsPortalOwner()
        >>> from zope.component import getMultiAdapter
        >>> view = getMultiAdapter((portal, portal.REQUEST),
        ...                         name=u'alchemy-tags.html')

        >>> print view()
        <...Use the form bellow to auto-discover and update...

    """

class Search(BrowserView):
    """ Search View

        >>> self.loginAsPortalOwner()
        >>> from zope.component import getMultiAdapter
        >>> view = getMultiAdapter((portal, portal.REQUEST),
        ...                         name=u'alchemy.search')

        >>> print view()
        <...Content-Types... ...Look in... ...Look for...

    """
    @property
    def portal_types(self):
        """ Available portal types
        """
        voc = queryUtility(IVocabularyFactory,
                           name=u"eea.faceted.vocabularies.FacetedPortalTypes")

        for term in voc(self.context):
            yield term

    @property
    def atschema(self):
        """ Archetypes base schema
        """
        voc = queryUtility(IVocabularyFactory,
                           name=u"eea.alchemy.vocabularies.SchemaAndCatalog")

        for term in voc(self.context):
            if not term.value:
                continue
            yield term

    @property
    def lookfor(self):
        """ Discoverable tags
        """
        voc = queryUtility(IVocabularyFactory,
                           name=u"eea.alchemy.vocabularies.DiscoverAdapters")
        for term in voc(self.context):
            yield term

class Update(BrowserView):
    """ Results View

        >>> self.loginAsPortalOwner()
        >>> from zope.component import getMultiAdapter
        >>> view = getMultiAdapter((portal, portal.REQUEST),
        ...                         name=u'alchemy.update')

        >>> print view.run()
        Auto-discover complete

    """

    def __init__(self, context, request):
        super(Update, self).__init__(context, request)
        self.action = 'preview'
        self.logger = None
        self.portal_type = ''
        self.lookin = 'Description'
        self.lookfor = 'subject'

    def setup(self):
        """ Setup server-sent events
        """
        # Custom logging
        formatter = logging.Formatter(
            "event: %(levelname)s\n"
            "data: %(asctime)s - %(name)s - %(levelname)s -  %(message)s\n\n")
        self.logger = logging.StreamHandler(self.request.response)
        self.logger.setLevel(logging.INFO)
        self.logger.setFormatter(formatter)
        logger.addHandler(self.logger)

        # Override response content-type
        self.request.response.setHeader(
            'Content-Type', 'text/event-stream; charset=utf-8')

    def cleanup(self):
        """ Cleanup server-sent events
        """
        # Close open connections and remove custom logger
        try:
            self.request.response.write('event: CLOSE\ndata: Done\n\n')
            logger.removeHandler(self.logger)
        except Exception, err:
            logger.exception(err)

    def run(self, **kwargs):
        """ Run a mini server-sent events
        """
        form = getattr(self.request, 'form', {})
        form.update(kwargs)

        action = form.get('action', 'Preview') or 'Preview'
        action = action.lower()
        portal_catalog = getToolByName(self.context, 'portal_catalog')
        portal_type = form.get('portal_type', None)
        brains = portal_catalog(Language='all', portal_type=portal_type)
        batch = form.get('alchemy-batch', '0-0')
        lookin = form.get('lookin', [])
        lookfor = form.get('lookfor', [])
        if isinstance(lookfor, (str, unicode)):
            lookfor = (lookfor,)

        start, end = (int(x) for x in batch.split('-'))
        logger.info("Content-Type: %s -- Lookin: %s -- "
                    "Lookfor: %s -- Batch: %s -- Action: %s",
            portal_type, lookin, lookfor, batch, action)

        for count, brain in enumerate(brains[start:end]):
            for name in lookfor:
                self.discover(brain, lookin, name)

            if (action == u'apply') and ((count + 1) % 10 == 0):
                logger.warn('Commit transaction %s/%s', count, end)
                transaction.commit()

        if action != u'apply':
            logger.warn("Preview mode selected, aborting transaction!")
            transaction.abort()
        return u'Auto-discover complete'

    def discover(self, brain, lookin, lookfor):
        """ Discover tags in brain
        """
        discover = queryAdapter(brain, IDiscoverAdapter, name=lookfor)
        if not discover:
            logger.warn('No %s adapter found for %s', lookfor, brain)
            return

        discover.metadata = lookin
        discover.tags = 'Update'

    def __call__(self, **kwargs):
        try:
            self.setup()
            self.run(**kwargs)
        except Exception, err:
            logger.exception(err)
        finally:
            self.cleanup()

class Batch(BrowserView):
    """ Batch info
    """

    def __call__(self, **kwargs):
        if self.request:
            kwargs.update(self.request.form)
        ptype = kwargs.get('portal_type', '')
        ctool = getToolByName(self.context, 'portal_catalog')
        brains = ctool(Language='all', portal_type=ptype)
        return len(brains)
