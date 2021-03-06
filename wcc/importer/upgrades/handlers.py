from collective.grok import gs
from Products.CMFCore.utils import getToolByName

# -*- extra stuff goes here -*- 


@gs.upgradestep(title=u'Upgrade wcc.importer to 1003',
                description=u'Upgrade wcc.importer to 1003',
                source='1002', destination='1003',
                sortkey=1, profile='wcc.importer:default')
def to1003(context):
    catalog = getToolByName(context, 'portal_catalog')
    catalog.delIndex('wcc_original_url')

    setup = getToolByName(context, 'portal_setup')
    setup.runAllImportStepsFromProfile('profile-wcc.importer.upgrades:to1003')


    catalog.reindexIndex('wcc_original_url', context.REQUEST)

@gs.upgradestep(title=u'Upgrade wcc.importer to 1002',
                description=u'Upgrade wcc.importer to 1002',
                source='1', destination='1002',
                sortkey=1, profile='wcc.importer:default')
def to1002(context):
    setup = getToolByName(context, 'portal_setup')
    setup.runAllImportStepsFromProfile('profile-wcc.importer.upgrades:to1002')

    catalog = getToolByName(context, 'portal_catalog')
    catalog.reindexIndex('wcc_id_url', context.REQUEST)
    catalog.reindexIndex('wcc_original_url', context.REQUEST)
