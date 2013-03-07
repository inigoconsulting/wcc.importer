from zope.interface import Interface
from zope.annotation.interfaces import IAnnotations
from plone.indexer.decorator import indexer

@indexer(Interface)
def wcc_original_url(context, **kw):
    try:
        anno = IAnnotations(context)
    except:
        raise AttributeError('wcc_original_url')
    if anno.has_key('wcc.metadata'):
        return anno['wcc.metadata']['original_url']
