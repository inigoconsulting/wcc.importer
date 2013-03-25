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
    grok.name('wcc.importer.descriptionsetter')

    def run_import(self, container, data):
        for l in data:
            self._factory(container, l)

    def _factory(self, container, entry):
        objs = []
        if entry.get('id_url', None):
            objs += self.find_objs_by_url(container, entry['id_url'])

        if entry.get('orig_url', None):
            objs += self.find_objs_by_url(container, entry['orig_url'])

        for i in set(objs):
            logger.info("Updating description of %s" % i.absolute_url())
            i.setDescription(entry['description'])
            i.reindexObject()
