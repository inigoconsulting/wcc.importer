from five import grok
import dateutil.parser
from zope.annotation.interfaces import IAnnotations
from persistent.dict import PersistentDict
import logging
logger = logging.getLogger("wcc.importer")
from base64 import b64decode
from wcc.importer.utility.base import BaseImporter
import urlparse
import os
from Acquisition import aq_parent
import transaction

def _clean_url(url):
    return url.replace('?print=1_%2F', '').replace('&print=1_%2F','')

class EWNSWWImporter(BaseImporter):
    grok.name('wcc.importer.ewnsevenweekwaterimporter')

    def run_import(self, container, data):
        tracker = []
        data = sorted(data, key=lambda x: x['orig_url'].count('/'))
        tx_pages = [i for i in data if 'tx_wecdiscussion' in i['orig_url']]
        data = [i for i in data if 'tx_wecdiscussion' not in i['orig_url']]
        for entry in data:
            cleanurl = _clean_url(entry['orig_url'])
            if cleanurl in tracker:
                continue
            self._factory(container, entry)
            tracker.append(cleanurl)

        for entry in sorted(tx_pages, key=lambda x: x['orig_url']):
            cleanurl = _clean_url(entry['orig_url'])
            if cleanurl in tracker:
                continue
            self._factory(container, entry)
            tracker.append(cleanurl)

    def _find_parent(self, container, orig_url):
        parent_url = os.path.dirname(orig_url) + '.html'
        if 'tx_wecdiscussion' in orig_url:
            parent_url = orig_url[:orig_url.find('?')]
        brains = container.portal_catalog(wcc_original_url=parent_url)
        if brains:
            return aq_parent(brains[0].getObject())
        return container

    def _factory(self, container, entry):
        logger.info("Creating EWNSWW Item : %s" % entry['title'])
        # find container
        parent = self._find_parent(container, entry['orig_url'])

        # create container folder
        oid = os.path.basename(
            urlparse.urlparse(entry['orig_url']).path.replace('.html','')
        )
        if 'tx_wecdiscussion' in entry['orig_url']:
            oid = entry['title']
        oid = self._create_obj_for_title(parent, 'Folder', oid)
        obj = parent._getOb(oid)
        obj.setTitle(entry['title'])

        # create page
        pageoid = self._create_obj_for_title(obj, 'Document', oid)
        page = obj._getOb(pageoid)
        page.setTitle(entry['title'])

        # set bodytext
        page.getField('text').set(page, entry['bodytext'])
        
        # set image
        if entry.get('image',None):
            try:
                page.getField('image').set(page, 
                        b64decode(entry['image']))
            except:
                logger.info(
                    "Unable to import image for : %s" % obj.absolute_url()
                )

        if entry.get('imageCaption', None):
            page.getField('imageCaption').set(page, entry['imageCaption'])


        # remember original url
        anno = IAnnotations(page)
        anno.setdefault('wcc.metadata', PersistentDict())
        anno['wcc.metadata']['original_url'] = entry['orig_url']
        anno['wcc.metadata']['lang_urls'] = entry['lang_urls']

        page.reindexObject()
        obj.reindexObject()
        transaction.savepoint(optimistic=True)

        logger.info("Created %s" % obj.absolute_url())
