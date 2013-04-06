from five import grok
from Products.CMFCore.interfaces import IFolderish
from Products.ATContentTypes.interfaces.folder import IATFolder
import json
from plone.directives import form
from collective.z3cform.grok.grok import PloneFormWrapper
import plone.autoform.form
import z3c.form.button
from plone.namedfile.field import NamedFile
from zope import schema
from wcc.importer import MessageFactory as _
from wcc.importer.interfaces import IProductSpecific, IImporter
from zope.component import getUtility
from Products.statusmessages.interfaces import IStatusMessage
from zope.annotation.interfaces import IAnnotations
import urlparse
from plone.app.redirector.interfaces import IRedirectionStorage
from zope.component import getUtility
from Products.CMFCore.interfaces import ISiteRoot
from plone.multilingual.interfaces import ITranslationManager
import logging
from pyquery import PyQuery
from wcc.importer.utils import clean_url

logger = logging.getLogger('wcc.importer')

grok.templatedir('templates')

class IUploadFormSchema(form.Schema):

    import_file = NamedFile(title=_('Upload import JSON'))
    importer = schema.Choice(title=_("Importer"),
            vocabulary="wcc.importer")

class UploadForm(form.SchemaForm):

    name = _("Import contents from JSON")
    schema = IUploadFormSchema
    ignoreContext = True
    grok.layer(IProductSpecific)
    grok.context(IFolderish)
    grok.name('import-contents')
    grok.require('cmf.AddPortalContent')


    @z3c.form.button.buttonAndHandler(_("Import"), name='import')
    def import_content(self, action):
        formdata, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        
        f = formdata['import_file'].data
        data = json.loads(f)

        importer = getUtility(IImporter, name=formdata['importer'])
        importer.run_import(self.context, data)
        IStatusMessage(self.request).addStatusMessage(_("Objects imported"))

    @z3c.form.button.buttonAndHandler(_("Setup redirects"),
                                        name='add-redirect')
    def add_redirect(self, action):
        if self.request.method != 'POST':
            return

        for i in self.context.portal_catalog(Language='all'):
            obj = i.getObject()
            anno = IAnnotations(obj).get('wcc.metadata', {})
            from_url = anno.get('original_url', None)
            id_url = anno.get('id_url', None)
            if not from_url:
                continue

            for url in from_url:
                self._add_redirect(url, obj)

            if id_url:
                self._add_redirect(id_url, obj)

        IStatusMessage(self.request).addStatusMessage(_("Redirection added"))

    def _add_redirect(self, from_url, obj):
        logger.info("Redirect %s to %s" % (from_url, obj.absolute_url()))
        from_url = urlparse.urlparse(from_url).path
        portal = getUtility(ISiteRoot)
        from_url = '/'.join(portal.getPhysicalPath()) + from_url
        to_url = '/'.join(obj.getPhysicalPath())
        storage = getUtility(IRedirectionStorage)
        if storage.has_path(from_url):
            storage.remove(from_url)
        storage.add(from_url, to_url)


    @z3c.form.button.buttonAndHandler(_("Map multilingual"),
                                name='map-multilingual')
    def map_multilingual(self, action):

        if self.request.method != 'POST':
            return

        for i in self.context.portal_catalog():
            obj = i.getObject()
            anno = IAnnotations(obj).get('wcc.metadata', {})
            if not anno.get('lang_urls', None):
                continue
            lang_urls = anno.get('lang_urls')
            logger.info('Setting language map for %s' % obj.absolute_url())
            for lang, url in lang_urls.items():
                brains = self.context.portal_catalog(Language='all',
                    wcc_original_url=clean_url(url))
                if not brains:
                    logger.info('No Objects Found! : %s' % url)
                    continue
                content = brains[0].getObject()
                ITranslationManager(obj).register_translation(lang, content)
        IStatusMessage(self.request).addStatusMessage(_("Mapping done"))

#    @z3c.form.button.buttonAndHandler(_("Auto set news description"),
#            name="set-newsdescription")
#    def set_newsdescription(self, action):
#        if self.request.method != 'POST':
#            return
#
#        for i in self.context.portal_catalog(portal_type="News Item",
#                                            Language='all'):
#            obj = i.getObject()
#            if obj.Description():
#               continue
#            logger.info("Setting description for %s" % obj.absolute_url())
#            text = obj.getText()
#            firstpara = PyQuery(text)('p:first').text()
#            obj.setDescription(firstpara)
#            obj.reindexObject()
#
#        IStatusMessage(self.request).addStatusMessage(_("Mapping done"))
