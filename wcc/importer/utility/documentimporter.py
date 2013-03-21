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
from Products.ATContentTypes.interfaces.folder import IATFolder
import os
import transaction
from Acquisition import aq_parent
from plone.namedfile.file import NamedBlobFile

class Importer(BaseImporter):
    grok.name('wcc.importer.documentimporter')

    def run_import(self, container, data):
        # cleanup urls

        newdata = []
        for entry in data:
            entry['orig_url'] = self._clean_url(entry['orig_url'])
            if entry.has_key('lang_urls'):
                entry['lang_urls'] = self._clean_langurls(entry['lang_urls'])

            # only include stuff in documents section
            for p in ['en/resources/documents', 'de/dokumentation/documents',
                    'fr/documentation/documents', 'es/documentacion/documents']:
                if p in entry['orig_url']:
                    newdata.append(entry)
                    break

        data = sorted(newdata, key=lambda x:x['orig_url'])

        folderish_urls  = set()
        for entry in data:
            folder_url = os.path.dirname(entry['orig_url']) + '.html'
            folderish_urls.add(folder_url)

        for entry in data:
            if entry['orig_url'] in folderish_urls:
                entry['is_folderish'] = True
            else:
                entry['is_folderish'] = False

        passed = []
        for entry in data:            
            if entry['orig_url'] in passed: 
                continue

            objcontainer = self._find_folder(container, entry)

            self._document_factory(objcontainer, entry)

            passed.append(entry['orig_url'])

    def _find_folder(self, container, entry):
        folder_url = os.path.dirname(entry['orig_url']) + '.html'
        if folder_url in [
                'http://oikoumene.org/en/resources/documents.html', 
                'http://oikoumene.org/de/dokumentation/documents.html',
                'http://oikoumene.org/fr/documentation/documents.html',
                'http://oikoumene.org/es/documentacion/documents.html',
                'http://www.oikoumene.org/en/resources/documents.html', 
                'http://www.oikoumene.org/de/dokumentation/documents.html',
                'http://www.oikoumene.org/fr/documentation/documents.html',
                'http://www.oikoumene.org/es/documentacion/documents.html'

            ]:
            return container

        brain = container.portal_catalog(wcc_original_url=folder_url)

        if not brain:
            title = os.path.dirname(entry['orig_url']).replace('.html','')
            title = os.path.basename(title)
            folder_entry = {
                'orig_url': folder_url,
                'title': title,
                'lang_urls':{},
                'id_url':None
            }

            folder = self._find_folder(container, folder_entry)
            return self._folder_factory(folder, folder_entry)
        else:
            result = brain[0].getObject()
            if not IATFolder.providedBy(result):
                return aq_parent(result)
            return result
        

    def _folder_factory(self, container, entry):
        logger.info("Creating Folder : %s" % entry['title'])

        oid = self._create_obj_for_title(container, 'Folder', entry['title'])
        obj = container._getOb(oid)

        anno = IAnnotations(obj)
        anno.setdefault('wcc.metadata', PersistentDict())
        anno['wcc.metadata']['original_url'] = entry['orig_url']
        anno['wcc.metadata']['lang_urls'] = entry['lang_urls']
        anno['wcc.metadata']['id_url'] = entry.get('id_url', None)

        obj.reindexObject()

        return obj


    def _document_factory(self, container, entry):
        logger.info("Creating Document : %s (%s)" % (entry['title'],
                                                     entry['orig_url']))

        name = os.path.basename(entry['orig_url']).replace('.html', '')

        parent = container

        if entry['is_folderish']:
            folderoid = self._create_obj_for_title(container, 'Folder', name)
            parent = container._getOb(folderoid)
            parent.setTitle(entry['title'])
            name = 'index'

        oid = self._create_obj_for_title(parent, 'wcc.document.document', name) 
        
        obj = parent._getOb(oid)
        obj.title = entry['title']

        # set description
        dcobj = IDublinCore(obj)
        dcobj.description = entry['description']

        # set effectiveDate
        edate = dateutil.parser.parse(entry['effectiveDate'])
        dcobj.effective = edate

        # set bodytext

        IBodyText(obj).text = entry.get('bodytext','')

        # set main fields

        obj.document_owner = entry['owner'].strip()
        obj.document_type = entry['document_type']
        obj.subjects = entry['related_descriptors']
        obj.document_status = entry['status']
        related_links = [{
            'url': i['url'],
            'label': i['title'],
            'description': i['description']
        } for i in entry['related_links']]
        obj.related_links = related_links

        if entry['file']:
            f = NamedBlobFile(
                    data = b64decode(entry['file']['data']),
                    filename=entry['file']['name']
            )
            obj.file = f
        
        # remember original url
        anno = IAnnotations(obj)
        anno.setdefault('wcc.metadata', PersistentDict())
        anno['wcc.metadata']['original_url'] = entry['orig_url']
        anno['wcc.metadata']['lang_urls'] = entry['lang_urls']
        anno['wcc.metadata']['id_url'] = entry.get('id_url', None)
        obj.reindexObject()

        if entry['is_folderish']:
            parent.setDefaultPage(oid)
            parent.reindexObject()

        logger.info("Created %s" % obj.absolute_url())
