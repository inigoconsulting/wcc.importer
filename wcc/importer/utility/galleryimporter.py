from five import grok
import dateutil.parser
from zope.annotation.interfaces import IAnnotations
from persistent.dict import PersistentDict
import logging
logger = logging.getLogger("wcc.importer")
from base64 import b64decode

from wcc.importer.utility.base import BaseImporter

class GalleryImporter(BaseImporter):
    grok.name('wcc.importer.galleryimporter')

    def run_import(self, container, data):
        for entry in data:
            self.create_gallery(container, entry)

    def create_gallery(self, container, entry):
        logger.info("Creating Gallery : %s" % entry['title'])

        # create folder
        oid = self._create_obj_for_title(container, 'Folder', entry['title'])
        obj = container._getOb(oid)

        # create images inside folder 
        for imgdata in entry['images']:
            imgoid = self._create_obj_for_title(obj, 'Image', imgdata['caption'])
            imgobj = obj._getOb(imgoid)
            imgobj.getField('image').set(imgobj, b64decode(imgdata['image']))
            imgobj.reindexObject()

        # create default view of folder
        pageoid = self._create_obj_for_title(obj, 'Document', 'index')
        pageobj = obj._getOb(pageoid)
        pageobj.setTitle(entry['title'])
        pageobj.getField('text').set(pageobj, entry['bodytext'])
        # obj.setDefaultPage(pageoid)
        obj.setLayout('atct_album_view')

        anno = IAnnotations(obj)
        anno.setdefault('wcc.metadata', PersistentDict())
        anno['wcc.metadata']['original_url'] = entry['orig_url']
        anno['wcc.metadata']['lang_urls'] = entry['lang_urls']

        pageobj.reindexObject()
        obj.reindexObject()

        logger.info("Created %s" % obj.absolute_url())

