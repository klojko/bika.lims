from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from bika.lims.permissions import AddMultifile
from Products.Archetypes.BaseContent import BaseContent
from bika.lims.upgrade import stub
from bika.lims import logger

def upgrade(tool):
    """Upgrade step required for Bika LIMS 3.1.9
    """
    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup

    # Friendly message
    qi = portal.portal_quickinstaller
    ufrom = qi.upgradeInfo('bika.lims')['installedVersion']
    logger.info("Upgrading Bika LIMS: %s -> %s" % (ufrom, '319'))

    # Updated profile steps
    # important info about upgrade steps in
    # http://stackoverflow.com/questions/7821498/is-there-a-good-reference-list-for-the-names-of-the-genericsetup-import-steps
    setup.runImportStepFromProfile('profile-bika.lims:default', 'typeinfo')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'jsregistry')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'cssregistry')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'workflow-csv')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'catalog')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'skins')

    # Update workflow permissions
    wf = getToolByName(portal, 'portal_workflow')
    wf.updateRoleMappings()

    # Migrations
    port_indexes_to_portal_catalog(portal)

    return True


def port_indexes_to_portal_catalog(portal):
    """ Consolidating indexes into portal_catalog
    https://jira.bikalabs.com/browse/LIMS-1851
    https://jira.bikalabs.com/browse/LIMS-1914
    https://jira.bikalabs.com/browse/LIMS-121
    """
    for cat in ("bika_catalog", "bika_analysis_catalog", "bika_setup_catalog"):
        if cat in portal:
            portal.manage_delObjects([cat,])

    at = getToolByName(portal, 'archetype_tool')

    # From bika catalog and bika analysis catalog
    at.setCatalogsByType('Analysis', ['portal_catalog'])
    at.setCatalogsByType('AnalysisRequest', ['portal_catalog'])
    at.setCatalogsByType('Batch', ['portal_catalog'])
    at.setCatalogsByType('Sample', ['portal_catalog'])
    at.setCatalogsByType('SamplePartition', ['portal_catalog'])
    at.setCatalogsByType('Worksheet', ['portal_catalog'])
    at.setCatalogsByType('DuplicateAnalysis', ['portal_catalog'])
    at.setCatalogsByType('ReferenceAnalysis', ['portal_catalog'])
    at.setCatalogsByType('Report', ['portal_catalog'])
    at.setCatalogsByType('ReferenceSample', ['portal_catalog'])

    # from bika setup catalog:
    at.setCatalogsByType('Department', ['portal_catalog'])
    at.setCatalogsByType('Container', ['portal_catalog'])
    at.setCatalogsByType('ContainerType', ['portal_catalog'])
    at.setCatalogsByType('AnalysisCategory', ['portal_catalog'])
    at.setCatalogsByType('AnalysisService', ['portal_catalog'])
    at.setCatalogsByType('AnalysisSpec', ['portal_catalog'])
    at.setCatalogsByType('SampleCondition', ['portal_catalog'])
    at.setCatalogsByType('SampleMatrix', ['portal_catalog'])
    at.setCatalogsByType('SampleType', ['portal_catalog'])
    at.setCatalogsByType('SamplePoint', ['portal_catalog'])
    at.setCatalogsByType('StorageLocation', ['portal_catalog'])
    at.setCatalogsByType('SamplingDeviation', ['portal_catalog'])
    at.setCatalogsByType('Instrument', ['portal_catalog'])
    at.setCatalogsByType('InstrumentType', ['portal_catalog'])
    at.setCatalogsByType('Method', ['portal_catalog'])
    at.setCatalogsByType('Multifile', ['portal_catalog'])
    at.setCatalogsByType('AttachmentType', ['portal_catalog'])
    at.setCatalogsByType('Calculation', ['portal_catalog'])
    at.setCatalogsByType('AnalysisProfile', ['portal_catalog'])
    at.setCatalogsByType('ARTemplate', ['portal_catalog'])
    at.setCatalogsByType('LabProduct', ['portal_catalog'])
    at.setCatalogsByType('LabContact', ['portal_catalog'])
    at.setCatalogsByType('Manufacturer', ['portal_catalog'])
    at.setCatalogsByType('Preservation', ['portal_catalog'])
    at.setCatalogsByType('ReferenceDefinition', ['portal_catalog'])
    at.setCatalogsByType('SRTemplate', ['portal_catalog'])
    at.setCatalogsByType('SubGroup', ['portal_catalog'])
    at.setCatalogsByType('Supplier', ['portal_catalog'])
    at.setCatalogsByType('Unit', ['portal_catalog'])
    at.setCatalogsByType('WorksheetTemplate', ['portal_catalog'])
    at.setCatalogsByType('BatchLabel', ['portal_catalog'])
    at.setCatalogsByType('ARPriority', ['portal_catalog'])
