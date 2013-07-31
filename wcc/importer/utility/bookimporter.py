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
from plone.namedfile import NamedBlobImage
import dateutil.parser
from z3c.relationfield import RelationValue
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility

class Importer(BaseImporter):
    grok.name('wcc.importer.bookimporter')


    def _get_author_id_map(self, container):
        m = {}
        for brain in container.portal_catalog(portal_type='wcc.books.author'):
            obj = brain.getObject()
            anno = IAnnotations(obj)
            anno.setdefault('wcc.metadata', PersistentDict())
            data = anno['wcc.metadata'].get('authordata', None)
            if data:
                m[data['id']] = obj
        return m


    def _factory(self, container, entry):

        author_id_map = self._get_author_id_map(container)

        logger.info("Creating Book : %s" % entry['title'])

        oid = self._create_obj_for_title(container, 'wcc.books.book', entry['title'])
        obj = container._getOb(oid)

        authors = []

        intids = getUtility(IIntIds)

        for authorid in entry['authors']:
            authorobj = author_id_map.get(authorid, None)
            if not authorobj:
                continue
            authors.append(RelationValue(intids.getId(authorobj)))

        obj.authors = authors
        obj.subtitle = entry['subtitle']
        obj.setTitle(entry['title'])
        obj.setSubject(entry['category'])
        obj.note = entry['note']
        obj.issue_date = dateutil.parser.parse(entry['issue_date'])
        obj.pages = entry.get('pages', None)
        if entry.get('image_data', ''):
            obj.image = NamedBlobImage(b64decode(entry['image_data']),
                filename=entry['image'])
        obj.series_title = entry.get('series title', None)
        obj.edition = entry.get('edition', None)
        obj.book_subjects = entry['subject']
        obj.toc = entry['toc']
        obj.price = float(entry.get('price', None) or 0)

        anno = IAnnotations(obj)
        anno.setdefault('wcc.metadata', PersistentDict())
        anno['wcc.metadata']['bookdata'] = entry

        logger.info("Created %s" % obj.absolute_url())
