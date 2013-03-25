from plone.app.layout.viewlets.common import ViewletBase
from zope.annotation.interfaces import IAnnotations
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class URLViewlet(ViewletBase):

    index = ViewPageTemplateFile('templates/urlviewlet.pt')

    def anno(self):
        anno = IAnnotations(self.context)
        return anno.get('wcc.metadata', {})

    def urls(self):
        anno = self.anno()
        orig_url = anno.get('original_url', [])
        return orig_url
