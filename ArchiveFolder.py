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
import Acquisition
from Products.CPSCore.CPSBase import CPSBaseDocument, CPSBase_adder
from OFS.Image import File
from zLOG import LOG, DEBUG
from StringIO import StringIO
from types import StringType
from zipfile import ZipFile
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate

_marker = []

factory_type_information = ({ 
    'id': 'CPSArchiveFolder',
    'meta_type': 'CPSArchiveFolder',
    'description': "portal_type_ArchiveFolder_description",
    'icon': 'folder_icon.gif',
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

    def edit(self, zip_file=None, zip_file_change=None, **kw):
        """Edit the object props."""
        if zip_file_change in ('change', None):
            if zip_file is not None:
                self._update(zip_file)
        elif zip_file_change == 'delete':
            self._file = None
            self._object_ids = ()
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
            raw = 0
            if id.endswith(".html.raw"):
                id = id[:-4]
                raw = 1

            zf = ZipFile(StringIO(str(self._file)))
            try:
                data = zf.read(id)
            except KeyError, id:
                if default is _marker:
                    raise AttributeError, id
                else:
                    return default

            if id.endswith(".html") and not raw and not self.new_window:
                return File(id, '', file=self.archivefolder_wrap_template(id=id)).__of__(self)
            
            else:
                return File(id, '', file=data).__of__(self)
            
        elif default is _marker:
            raise AttributeError, id
        else:
            return default

