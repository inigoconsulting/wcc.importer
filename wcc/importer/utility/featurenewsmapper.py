from five import grok
import dateutil.parser
from zope.annotation.interfaces import IAnnotations
from persistent.dict import PersistentDict
import logging
logger = logging.getLogger("wcc.importer")
from base64 import b64decode
from wcc.importer.utility.base import BaseImporter
from wcc.featurable.interfaces import IFeaturable

class FeatureNewsMapper(BaseImporter):
    grok.name('wcc.importer.featurenewsmapper')

    def _factory(self, container, entry):
            
        catalog = container.portal_catalog
        result = catalog(wcc_original_url=entry['orig_url'])
        if not result:
            result = catalog(wcc_id_url=entry['id_url'])
        if not result:
            logger.info("No Object Found! %s" % entry['orig_url'])
        for brain in result:
            obj = brain.getObject()
            if not IFeaturable.providedBy(obj):
                logger.info(
                    "%s does not provide IFeaturable" % obj.absolute_url())
            obj.is_featured = True
            obj.reindexObject()
            logger.info("Featuring: %s" % obj.absolute_url())

