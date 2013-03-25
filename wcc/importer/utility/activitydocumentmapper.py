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
from z3c.relationfield import RelationValue
from wcc.activity.behavior.activitytag import IActivityTag
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility
from plone.dexterity.interfaces import IDexterityContent
from Products.ATContentTypes.interfaces import IATContentType
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent

class Importer(BaseImporter):
    grok.name('wcc.importer.activitydocumentmapper')

    def run_import(self, container, data):
        self._objects = set()
        for l in data:
            self._factory(container, l)
        for o in self._objects:
            o.reindexObject()
            notify(ObjectModifiedEvent(o))
        
    def _factory(self, container, entry):
        for i in self.find_objs_by_url(container, entry['orig_url']):
            print "Found %s" % i.absolute_url()
            self._objects.add(i)

            if IDexterityContent.providedBy(i):
                self._dexterity_apply(container, i, entry)
                continue

            if IATContentType.providedBy(i):
                self._atct_apply(container, i, entry)

    def _dexterity_apply(self, container, obj, entry):
        adapted = IActivityTag(obj)
        intids = getUtility(IIntIds)
        for c in entry['related_activities']:
            vals = getattr(obj, 'related_activities', []) or []
            valobjs = [k.to_object for k in vals]
            for a in self.find_objs_by_url(container, c):
                if a in valobjs:
                    continue
                logger.info("Mapping %s to %s" % (obj.absolute_url(),
                                                a.absolute_url()))
                vals.append(RelationValue(intids.getId(a)))
            adapted.related_activities = vals

    def _atct_apply(self, container, obj, entry):
        for c in entry['related_activities']:
            field = obj.getField('related_activities')
            vals = field.get(obj)
            for a in self.find_objs_by_url(container, c):
                if a in vals:
                    continue
                logger.info("Mapping %s to %s" % (obj.absolute_url(),
                                                a.absolute_url()))
                vals.append(a)
            field.set(obj, vals)

