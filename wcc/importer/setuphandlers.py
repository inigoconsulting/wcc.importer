from collective.grok import gs
from wcc.importer import MessageFactory as _

@gs.importstep(
    name=u'wcc.importer', 
    title=_('wcc.importer import handler'),
    description=_(''))
def setupVarious(context):
    if context.readDataFile('wcc.importer.marker.txt') is None:
        return
    portal = context.getSite()

    # do anything here
