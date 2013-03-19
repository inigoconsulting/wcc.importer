from five import grok
import dateutil.parser
from zope.annotation.interfaces import IAnnotations
from persistent.dict import PersistentDict
import logging
logger = logging.getLogger("wcc.importer")
from base64 import b64decode
from wcc.importer.utility.base import BaseImporter
from wcc.featurable.interfaces import IFeaturable

class IDUrlImporter(BaseImporter):
    grok.name('wcc.importer.idurlimporter')

    def _factory(self, container, entry):

        if not entry.has_key('id_url'):
            return 
           
        catalog = container.portal_catalog
        result = catalog(wcc_original_url=entry['orig_url'], Language='all')

        if not result:
            logger.info("No Object Found! %s" % entry['orig_url'])
            return

        for brain in result:
            obj = brain.getObject()
            logger.info('Setting ID URL in : %s' % obj.absolute_url())
            anno = IAnnotations(obj)
            anno.setdefault('wcc.metadata', PersistentDict())
            anno['wcc.metadata']['id_url'] = entry['id_url']
            obj.reindexObject()
