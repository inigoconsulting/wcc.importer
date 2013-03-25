from plone.app.layout.viewlets.common import ViewletBase
from zope.annotation.interfaces import IAnnotations
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class URLViewlet(ViewletBase):

    index = ViewPageTemplateFile('templates/urlviewlet.pt')

    def anno(self):
        anno = IAnnotations(self.context)
        return anno.get('wcc.metadata', {})

    def urls(self):
        result = []
        anno = self.anno()
        orig_url = anno.get('original_url', None)
        if orig_url:
            result.append(orig_url)

        id_url = anno.get('id_url', None)
        if id_url:
            result.append('http://www.oikoumene.org%s' % id_url)

        return result
