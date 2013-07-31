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
    grok.name('wcc.importer.authorimporter')

    def _factory(self, container, entry):

        title = '%s %s' % (entry['name'], entry['surname'])

        logger.info("Creating Author : %s" % title)

        oid = self._create_obj_for_title(container, 'wcc.books.author', title)
        obj = container._getOb(oid)

        obj.setTitle(title)
        obj.name = entry['name']
        obj.surname = entry['surname']
        obj.biography = entry['biography']

        anno = IAnnotations(obj)
        anno.setdefault('wcc.metadata', PersistentDict())
        anno['wcc.metadata']['authordata'] = entry

        logger.info("Created %s" % obj.absolute_url())
