# (C) Copyright 2002, 2003 Nuxeo SARL <http://nuxeo.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
# $Id$

from AccessControl import ClassSecurityInfo
from Products.CMFCore.CMFCorePermissions import View, \
     ModifyPortalContent
from Products.CPSCore.CPSBase import CPSBaseDocument, CPSBase_adder
from OFS.Image import File
from zLOG import LOG, DEBUG
from StringIO import StringIO
from types import StringType
from zipfile import ZipFile
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate

_marker = []

wrap_template = """<metal:block define-macro="folder_view">
<metal:block use-macro="here/main_template/macros/master">
<metal:block fill-slot="main">
<h1 tal:content="here/title_or_id">Page Title</h1>
<div class="description"><span
  tal:content="here/Description">description</span>
</div>
%s
</metal:block>
</metal:block>
</metal:block>
"""

factory_type_information = ({ 
    'id': 'CPSArchiveFolder',
    'meta_type': 'CPSArchiveFolder',
    'description': "portal_type_ArchiveFolder_description",
    'icon': '',
    'title': "portal_type_ArchiveFolder_title",
    'product': 'CPSArchiveFolder',
    'factory': 'addCPSArchiveFolder',
    'immediate_view': 'archivefolder_edit_form',
    'allow_discussion': 0,
    'actions': ({
        'id': 'view',
        'name': 'action_view',
        'action': 'archivefolder_view',
        'permissions': (View,),
    }, {
        'id': 'edit',
        'name': 'action_modify',
        'action': 'archivefolder_edit_form',
        'permissions': (ModifyPortalContent,),
    },),
},)

def addCPSArchiveFolder(self, id, **kw):
    """
    Add an Archive Folder
    """
    obj = CPSArchiveFolder(id, **kw)
    CPSBase_adder(self, obj)

class CPSArchiveFolder(CPSBaseDocument):
    """
    Archive (ZIP, TGZ) folder
    """
    meta_type = 'CPSArchiveFolder'
    portal_type = 'CPSArchiveFolder'
    allow_discussion = 0
    security = ClassSecurityInfo()

    _properties = CPSBaseDocument._properties +\
       ( {'id': 'new_window', 'type': 'boolean', 'mode': 'w',
          'label': 'Open in new window'},
       )
 
    new_window = 0

    _file = None
    _object_ids = ()

    def __init__(self, id, file='', **kw):
        """Constructor"""
        self._update(file)
        CPSBaseDocument.__init__(self, id, **kw)

    def edit(self, fichier=None, fichier_change=None, **kw):
        """Edit the object props."""
        if fichier_change in ('change', None):
            if fichier is not None:
                self._update(fichier)
        elif fichier_change == 'delete':
            self.fichier = None
        CPSBaseDocument.edit(self, **kw)

    def _update(self, file):
        if not file:
            return

        self._file = File('zipdata', '', file=file)
        zf = ZipFile(StringIO(str(self._file)))
        infolist = zf.infolist()
        ids = []
        for info in infolist:
            if not info.filename.count('/'):
                ids.append(info.filename)
        self._object_ids = tuple(ids)

    def __getitem__(self, id):
        return self._getOb(id)

    def objectIds(self, spec=None):
        return self._object_ids

    def objectValues(self, spec=None):
        return [ self._getOb(id) for id in self._object_ids ]

    def objectItems(self, spec=None):
        return [ (id, self._getOb(id)) for id in self._object_ids ]

    def _getOb(self, id, default=_marker):
        if self._file:
            zf = ZipFile(StringIO(str(self._file)))
            data = zf.read(id)
            # Wrap into main template if not index.html
            # A bit ugly for now, but ok for testing purposes
            # XXX Direct call to ZopePageTemplate class ; is this OK ?
            if id.endswith(".html") and id != 'index.html':
                data = wrap_template % data
                return ZopePageTemplate(id='_zpt', text=data).__of__(self)

            return File(id, '', data).__of__(self)
        elif default is _marker:
            raise AttributeError, id
        return default

