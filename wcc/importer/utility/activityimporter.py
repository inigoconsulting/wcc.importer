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
    grok.name('wcc.importer.activityimporter')

    def _factory(self, container, entry):
        logger.info("Creating Activity : %s" % entry['title'])

        oid = self._create_obj_for_title(container, 'wcc.activity.activity', entry['title'])
        obj = container._getOb(oid)

        # set description
        IDublinCore(obj).description = entry['description']

        # set effectiveDate
#        edate = dateutil.parser.parse(entry['effectiveDate'])
#        obj.getField('effectiveDate').set(obj, edate)

        # set bodytext
        IBodyText(obj).text = entry['bodytext']
        
        # remember original url
        anno = IAnnotations(obj)
        anno.setdefault('wcc.metadata', PersistentDict())
        anno['wcc.metadata']['original_url'] = entry['orig_url']
        anno['wcc.metadata']['lang_urls'] = entry['lang_urls']
        anno['wcc.metadata']['id_url'] = entry.get('id_url', None)
        obj.reindexObject()

        logger.info("Created %s" % obj.absolute_url())
