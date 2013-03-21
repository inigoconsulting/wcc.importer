from five import grok
import dateutil.parser
from zope.annotation.interfaces import IAnnotations
from persistent.dict import PersistentDict
import logging
logger = logging.getLogger("wcc.importer")
from base64 import b64decode
from wcc.importer.utility.base import BaseImporter

class Importer(BaseImporter):
    grok.name('wcc.importer.titlesetter')

    def _factory(self, container, entry):
        logger.info("Updating title of : %s" % entry['orig_url'])
        
        for brain in container.portal_catalog(wcc_original_url=entry['orig_url'],
                Language='all'):
            obj = brain.getObject()
            obj.setTitle(entry['title'])
            obj.reindexObject()



