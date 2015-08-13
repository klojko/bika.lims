# coding=utf-8
from AccessControl import getSecurityManager
from Products.CMFPlone.utils import _createObjectByType
from Products.CMFPlone.utils import safe_unicode
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.permissions import EditResults, EditWorksheet, ManageWorksheets
from bika.lims import PMF, logger
from bika.lims.browser import BrowserView
from bika.lims.browser.analyses import AnalysesView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.browser.bika_listing import WorkflowAction
from bika.lims.browser.referencesample import ReferenceSamplesView as BaseView
from bika.lims.exportimport import instruments
from bika.lims.interfaces import IFieldIcons
from bika.lims.interfaces import IWorksheet
from bika.lims.subscribers import doActionFor
from bika.lims.subscribers import skip
from bika.lims.utils import to_utf8
from bika.lims.utils import getUsers, isActive, tmpID
from DateTime import DateTime
from DocumentTemplate import sequence
from operator import itemgetter
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.public import DisplayList
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import adapts
from zope.component import getAdapters
from zope.component import getMultiAdapter
from zope.interface import implements
from bika.lims.browser.referenceanalysis import AnalysesRetractedListReport
from DateTime import DateTime
from Products.CMFPlone.i18nl10n import ulocalized_time
from bika.lims.utils import to_utf8 as _c

import plone
import plone.protect
import json


class ReferenceSamplesView(BaseView):
    """ Display reference samples matching services in this worksheet
        add_blank and add_control use this to refresh the list of reference
        samples when service checkboxes are selected
    """
    implements(IViewView)

    def __init__(self, context, request):
        super(ReferenceSamplesView, self).__init__(context, request)
        self.catalog = 'bika_catalog'
        self.contentFilter = {'portal_type': 'ReferenceSample'}
        self.context_actions = {}
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_all_checkbox = False
        self.show_select_column = False
        self.show_workflow_action_buttons = False
        self.pagesize = 50
        # must set service_uids in __call__ before delegating to super
        self.service_uids = []
        # must set control_type='b' or 'c' in __call__ before delegating
        self.control_type = ""
        self.columns['Services'] = {'title': _('Services')}
        self.columns['Definition'] = {'title': _('Reference Definition')}
        self.review_states = [
            {'id':'default',
             'title': _('All'),
             'contentFilter':{'review_state':'current'},
             'columns': ['ID',
                         'Title',
                         'Definition',
                         'ExpiryDate',
                         'Services']
             },
        ]

    def __call__(self):
        self.service_uids = self.request.get('service_uids', '').split(",")
        self.control_type = self.request.get('control_type', '')
        if not self.control_type:
            return t(_("No control type specified"))
        return super(ReferenceSamplesView, self).contents_table()

    def folderitems(self):
        translate = self.context.translate
        workflow = getToolByName(self.context, 'portal_workflow')
        items = super(ReferenceSamplesView, self).folderitems()
        new_items = []
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            if self.control_type == 'b' and not obj.getBlank(): continue
            if self.control_type == 'c' and obj.getBlank(): continue
            ref_services = obj.getServices()
            ws_ref_services = [rs for rs in ref_services if
                               rs.UID() in self.service_uids]
            if ws_ref_services:
                if workflow.getInfoFor(obj, 'review_state') != 'current':
                    continue
                services = [rs.Title() for rs in ws_ref_services]
                items[x]['nr_services'] = len(services)
                items[x]['Definition'] = (obj.getReferenceDefinition() and obj.getReferenceDefinition().Title()) or ''
                services.sort(lambda x, y: cmp(x.lower(), y.lower()))
                items[x]['Services'] = ", ".join(services)
                items[x]['replace'] = {}

                after_icons = "<a href='%s' target='_blank'><img src='++resource++bika.lims.images/referencesample.png' title='%s: %s'></a>" % \
                    (obj.absolute_url(), \
                     t(_("Reference sample")), obj.Title())
                items[x]['before']['ID'] = after_icons

                new_items.append(items[x])

        new_items = sorted(new_items, key = itemgetter('nr_services'))
        new_items.reverse()

        return new_items
