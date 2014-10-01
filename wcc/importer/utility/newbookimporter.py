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
from z3c.relationfield import RelationValue
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility
import datetime


class Importer(BaseImporter):
    grok.name('wcc.importer.newbookimporter')

    def _get_author_id_map(self, container):
        m = {}
        for brain in container.portal_catalog(portal_type='wcc.books.author'):
            obj = brain.getObject()
            anno = IAnnotations(obj)
            anno.setdefault('wcc.metadata', PersistentDict())
            data = anno['wcc.metadata'].get('authordata', None)
            if data:
                m[data[u'By (author)']] = obj
        return m

    def _factory(self, container, entry):

        author_id_map = self._get_author_id_map(container)

        logger.info("Creating Book : %s" % entry['Title'])

        oid = self._create_obj_for_title(
            container, 'wcc.books.book', entry['Title'])
        obj = container._getOb(oid)

        authors = []

        intids = getUtility(IIntIds)

        authorid = entry['By (author)']

        if ',' in authorid:
            multiauthor = authorid.split(',')

            for i in multiauthor:
                authorobj = author_id_map.get(i, None)
                if not authorobj:
                    continue
                authors.append(RelationValue(intids.getId(authorobj)))

        else:
            authorobj = author_id_map.get(authorid, None)
            authors.append(RelationValue(intids.getId(authorobj)))

        obj.authors = authors
        obj.subtitle = entry.get('Sub-title', None)
        obj.setTitle(entry['Title'])
        obj.setSubject(entry['Subjects'])

        obj.issue_date = dateutil.parser.parse(
            entry['Published'],
            fuzzy=True, default=datetime.date.today().min)

        obj.pages = int(entry.get('pages', None) or 0)
        if entry.get('image', ''):
            obj.image = NamedBlobImage(b64decode(entry['image']),
                                       filename=entry['image'])
        obj.series_title = entry.get('Series', None)
        obj.edition = entry.get('Edition Statement', None)
        obj.book_subjects = entry['Subjects']
        obj.toc = entry.get('Table of Contents', None)
        obj.price = float(entry.get('Price', None) or 0)
        obj.isbn = entry.get('ISBN13', None)

        anno = IAnnotations(obj)
        anno.setdefault('wcc.metadata', PersistentDict())
        anno['wcc.metadata']['bookdata'] = entry

        logger.info("Created %s" % obj.absolute_url())
