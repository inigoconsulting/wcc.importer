from five import grok
from wcc.importer.interfaces import IImporter
from zope.container.interfaces import INameChooser
import time
import transaction
from plone.dexterity.fti import DexterityFTI
from plone.dexterity.utils import createContentInContainer
import urlparse
import urllib

class BaseImporter(grok.GlobalUtility):
    grok.implements(IImporter)
    grok.baseclass()

    def run_import(self, container, data):
        passed = []
        for entry in data:
            entry['orig_url'] = self._clean_url(entry['orig_url'])
            if entry.has_key('lang_urls'):
                entry['lang_urls'] = self._clean_langurls(entry['lang_urls'])

            if entry['orig_url'] in passed:
                continue

            self._factory(container, entry)
            passed.append(entry['orig_url'])


    def _clean_url(self, url):
        parsed = urlparse.urlparse(url)
        qs = parsed.query
        if not qs:
            return url
        qs = urlparse.parse_qs(qs)
        for v in ['print', 'cHash']:
            if qs.has_key(v):
                del qs[v]
        qs = sorted(qs.items(), key=lambda x: x[0])
        qs = [(k,v[0]) for k,v in qs]
        qs = urllib.urlencode(qs)
        data = list(parsed)
        data[4] = qs
        return urlparse.urlunparse(data)

    def _clean_langurls(self, lang_urls):
        newdict = {}
        for k, v in lang_urls.items():
            newdict[k] = self._clean_url(v)
        return newdict


    def _factory(self):
        raise NotImplementedError

    def _create_obj_for_title(self, container, portal_type, title):
        fti = container.portal_types.get(portal_type)

        if isinstance(fti, DexterityFTI):
            obj = createContentInContainer(container, portal_type, title=title) 
            transaction.savepoint(optimistic=True)
            return obj.id

        oid = container.invokeFactory(type_name=portal_type, id=time.time())

        transaction.savepoint(optimistic=True)

        obj = container._getOb(oid)
        # set id
        oid = INameChooser(container).chooseName(title, obj)

        obj.setId(oid)
        obj.setTitle(title)

        return oid


