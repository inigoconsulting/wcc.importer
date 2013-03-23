import urlparse
import urllib

def clean_url(url)
    parsed = urlparse.urlparse(url)
    qs = parsed.query
    if not qs:
        return url
    qs = urlparse.parse_qs(qs)
    for v in ['print', 'tx_ttnews[cat]']:
        if qs.has_key(v):
            del qs[v]
    qs = sorted(qs.items(), key=lambda x: x[0])
    qs = [(k,v[0]) for k,v in qs]
    qs = urllib.urlencode(qs)
    data = list(parsed)
    data[4] = qs
    result = urlparse.urlunparse(data)

    for i in range(0,100):
        s = '/browse/%s/' % i
        if s in result:
            result = result.replace(s, '/')
            break

    return result

