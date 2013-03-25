from zope.interface import Interface
from zope.annotation.interfaces import IAnnotations
from plone.indexer.decorator import indexer
from wcc.importer.utils import clean_url
from Products.CMFCore.interfaces import IContentish

@indexer(IContentish)
def wcc_original_url(context, **kw):
    try:
        anno = IAnnotations(context)
    except:
        raise AttributeError('wcc_original_url')
    if not anno.has_key('wcc.metadata'):
        raise AttributeError('wcc_original_url')
    if not anno['wcc.metadata'].has_key('original_url'):
        raise AttributeError('wcc_original_url')

    url = anno['wcc.metadata']['original_url']
    if isinstance(url, basestring):
        anno['wcc.metadata']['original_url'] = [url]

    urls = []
    for u in anno['wcc.metadata']['original_url']:
        urls.append(clean_url(u))

    if anno['wcc.metadata'].has_key('id_url'):
        if anno['wcc.metadata']['id_url']:
            urls.append(anno['wcc.metadata']['id_url'])
            urls.append('http://www.oikoumene.org' + anno['wcc.metadata']['id_url'])

    anno['wcc.metadata']['original_url'] = list(set(urls))
    anno['wcc.metadata'].p_changed = True
    return anno['wcc.metadata']['original_url']

@indexer(IContentish)
def wcc_id_url(context, **kw):
    try:
        anno = IAnnotations(context)
    except:
        raise AttributeError('wcc_id_url')
    if anno.has_key('wcc.metadata') and anno['wcc.metadata'].has_key('id_url'):
        if anno['wcc.metadata']['id_url']:
            return anno['wcc.metadata']['id_url']
    raise AttributeError('wcc_id_url')
