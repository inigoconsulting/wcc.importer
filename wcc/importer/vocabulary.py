from five import grok
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.schema.interfaces import IVocabularyFactory
from zope.component import getUtility
from z3c.formwidget.query.interfaces import IQuerySource
from zope.intid.interfaces import IIntIds
from zope.component import getUtility, getUtilitiesFor
from wcc.importer.interfaces import IImporter

class ImporterVocabulary(object):

    def __call__(self, context):
        terms = [SimpleTerm(value=i) for i, u in getUtilitiesFor(IImporter)]
        return SimpleVocabulary(terms)


grok.global_utility(ImporterVocabulary, IVocabularyFactory,
    name="wcc.importer")
