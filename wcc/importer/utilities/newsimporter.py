from five import grok
from wcc.importer.interfaces import IImporter
from zope.container.interfaces import INameChooser
import time
import transaction
import dateutil.parser
from zope.annotation.interfaces import IAnnotations
from persistent.dict import PersistentDict
from wcc.importer.interfaces import IImporter
import logging
logger = logging.getLogger("wcc.importer")
from base64 import b64decode

class NewsImporter(grok.GlobalUtility):
    grok.name('wcc.importer.newsimporter')
    grok.implements(IImporter)
    grok.require('cmf.AddPortalContent')

    def run_import(self, container, data):
        for entry in data:
            self.create_news(container, entry)

    def create_news(self, container, entry):
        logger.info("Creating News Item : %s" % entry['title'])

        oid = container.invokeFactory(type_name="News Item", id=time.time())
        transaction.savepoint(optimistic=True)
        obj = container._getOb(oid)

        # set id
        oid = INameChooser(container).chooseName(entry['title'], obj)
        obj.setId(oid)

        # set title

        obj.setTitle(entry['title'])

        # set effectiveDate
        d,m,y = entry['effectiveDate'].split('.')
        edate = dateutil.parser.parse('%s-%s-%s' % (y,m,d))
        obj.getField('effectiveDate').set(obj, edate)

        # set bodytext
        obj.getField('text').set(obj, entry['bodytext'])
        
        # set image
        if entry.has_key('image'):
            try:
                obj.getField('image').set(obj, 
                        b64decode(entry['image']))
            except:
                logger.info(
                    "Unable to import image for : %s" % obj.absolute_url()
                )

        if entry.has_key('imageCaption'):
            obj.getField('imageCaption').set(obj, entry['imageCaption'])

        # remember original url
        anno = IAnnotations(obj)
        anno.setdefault('wcc.metadata', PersistentDict())
        anno['wcc.metadata']['original_url'] = entry['orig_url']
        obj.reindexObject()

        logger.info("Created %s" % obj.absolute_url())
