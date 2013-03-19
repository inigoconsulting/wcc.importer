from five import grok
import dateutil.parser
from zope.annotation.interfaces import IAnnotations
from persistent.dict import PersistentDict
import logging
logger = logging.getLogger("wcc.importer")
from base64 import b64decode
from wcc.importer.utility.base import BaseImporter

class RawHTMLImporter(BaseImporter):
    grok.name('wcc.importer.rawhtmlimporter')

    def _factory(self, container, entry):
        logger.info("Creating RAWHTML Item : %s" % entry['title'])

        oid = self._create_obj_for_title(container, 'wcc.rawhtml.rawhtml',
                entry['name'])
        obj = container._getOb(oid)

        obj.title = entry['title']
        obj.raw_html = entry['raw_html']
        obj.type_tag = entry['type_tag']

        # remember original url
        anno = IAnnotations(obj)
        anno.setdefault('wcc.metadata', PersistentDict())
        anno['wcc.metadata']['original_url'] = entry['orig_url']
        anno['wcc.metadata']['lang_urls'] = entry['lang_urls']
        anno['wcc.metadata']['id_url'] = entry.get('id_url', None)
        obj.reindexObject()

        logger.info("Created %s" % obj.absolute_url())
