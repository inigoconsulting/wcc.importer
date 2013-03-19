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
        for i in self.context.portal_catalog(Language='all'):
            obj = i.getObject()
            anno = IAnnotations(obj).get('wcc.metadata', {})
            from_url = anno.get('original_url', None)
            id_url = anno.get('id_url', None)
            if not from_url:
                continue
            logger.info("Setting redirects for %s" % obj.absolute_url())
            from_url = urlparse.urlparse(from_url).path
            portal = getUtility(ISiteRoot)
            from_url = '/'.join(portal.getPhysicalPath()) + from_url
            if id_url:
                id_url = '/'.join(portal.getPhysicalPath()) + id_url
            to_url = '/'.join(obj.getPhysicalPath())
            storage = getUtility(IRedirectionStorage)
            if storage.has_path(from_url):
                storage.remove(from_url)
            if id_url and storage.has_path(id_url):
                storage.remove(id_url)
            storage.add(from_url, to_url)
            if id_url:
                storage.add(id_url, to_url)
        IStatusMessage(self.request).addStatusMessage(_("Redirection added"))

    @z3c.form.button.buttonAndHandler(_("Map multilingual"),
                                name='map-multilingual')
    def map_multilingual(self, action):
        for i in self.context.portal_catalog():
            obj = i.getObject()
            anno = IAnnotations(obj).get('wcc.metadata', {})
            if not anno.get('lang_urls', None):
                continue
            lang_urls = anno.get('lang_urls')
            logger.info('Setting language map for %s' % obj.absolute_url())
            for lang, url in lang_urls.items():
                brains = self.context.portal_catalog(Language='all',
                    wcc_original_url=url)
                if not brains:
                    logger.info('No Objects Found! : %s' % url)
                    continue
                content = brains[0].getObject()
                ITranslationManager(obj).register_translation(lang, content)
