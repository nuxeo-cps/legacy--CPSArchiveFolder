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
from OFS.Folder import Folder
from zLOG import LOG, DEBUG
from StringIO import StringIO
from zipfile import ZipFile

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
    'cps_is_searchable': 1,
},)

def addCPSArchiveFolder(self, id, **kw):
    """
    Add an Archive Folder
    """
    obj = CPSArchiveFolder(id, **kw)
    CPSBase_adder(self, obj)

class CPSArchiveFolder(CPSBaseDocument, Folder):
    """
    Archive (ZIP, TGZ) folder
    """
    meta_type = 'CPSArchiveFolder'
    portal_type = 'CPSArchiveFolder'
    allow_discussion = 0
    security = ClassSecurityInfo()

    new_window = 0
    _properties = CPSBaseDocument._properties + \
       ( {'id': 'new_window', 'type': 'boolean', 'mode': 'w',
          'label': 'Open in new window'},
       )

    _file = None

    def __init__(self, id, file='', **kw):
        """Constructor"""
        self._update(file)
        CPSBaseDocument.__init__(self, id, **kw)

    # XXX: what do we need here ?
    def index_html(self):
        """Default view"""
        if hasattr(self, "index.html"):
            # FIXME: ???
            #print getattr(self, "index.html")()
            #return getattr(self, "index.html")()
            pass
        else:
            # FIXME: ???
            pass

    def edit(self, zip_file=None, zip_file_change=None, **kw):
        """Edit the object properties."""
        if zip_file_change in ('change', None):
            if zip_file is not None:
                self._update(zip_file)
        elif zip_file_change == 'delete':
            self._file = None
            self.manage_delObjects(self.objectIds())
        CPSBaseDocument.edit(self, **kw)

    def _update(self, file):
        """Update content from zip file."""
        if not file:
            return
        self._file = File('zipdata', '', file=file)
        zipfile = ZipFile(StringIO(str(self._file)))
        infolist = zipfile.infolist()
        for info in infolist:
            path = info.filename
            # Skip folders
            if path[-1] == '/':
                continue
            data = zipfile.read(path)
            self._install(path, data)

    def _install(self, path, data):
        """Install object (file) <path> with content <data>."""
        l = path.split("/")
        folder = self
        for id in l[0:-1]:
            if not hasattr(folder, id):
                subfolder = Folder(id)
                folder._setObject(id, subfolder)
            folder = getattr(folder, id)
        id = l[-1]
        file = File(id, '', file=data)
        folder._setObject(id, file)

