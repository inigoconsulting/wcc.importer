from five import grok
import dateutil.parser
from zope.annotation.interfaces import IAnnotations
from persistent.dict import PersistentDict
import logging
logger = logging.getLogger("wcc.importer")
from base64 import b64decode
from wcc.importer.utility.base import BaseImporter
from plone.app.dexterity.behaviors.metadata import IDublinCore
from collective.miscbehaviors.behavior.bodytext import IBodyText


class Importer(BaseImporter):
    grok.name('wcc.importer.activitynewsmapper')

    def run_import(self, container, data):
        for l in data:
            self._factory(container, l)

    def _factory(self, container, entry):
        for i in self.find_objs_by_idurl(container, entry['id_url']):
            for c in entry['categories']:
                field = i.getField('related_activities')
                vals = field.get(i)
                for a in self.find_objs_by_idurl(container, c):
                    if a in vals:
                        continue
                    logger.info("Mapping %s to %s" % (i.absolute_url(),
                                                    a.absolute_url()))
                    vals.append(a)
                field.set(i, vals)
            i.reindexObject()

    def find_objs_by_idurl(self, container, url):
        brains = container.portal_catalog(wcc_id_url=url)
        result = []
        for brain in brains:
             result.append(brain.getObject())
        return result
