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
