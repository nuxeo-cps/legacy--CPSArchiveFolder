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

from zLOG import LOG, DEBUG
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.CMFCore.CMFCorePermissions import View, ModifyPortalContent
import ExtensionClass
import Acquisition
from webdav.common import rfc1123_date
from Acquisition import aq_parent, aq_inner
from Products.CPSCore.CPSBase import CPSBaseDocument, CPSBase_adder
from OFS.Image import File
from OFS.Folder import Folder
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


class FileEncapsulator(Acquisition.Explicit):
    """File encapsulator

    Does rendering of the file encapsulated in a template.
    """
    security = ClassSecurityInfo()
    security.declareObjectPublic()
    security.setDefaultAccess('allow')

    meta_type = 'FileEncapsulator'

    def __init__(self, file, context):
        self.file = file
        self.context = context

    def index_html(self, REQUEST, RESPONSE):
        """Publish the file, encapsulated by archivefolder_wrap."""
        file = self.file
        content = self.context.archivefolder_wrap(html=str(file))
        RESPONSE.setHeader('Last-Modified', rfc1123_date(file._p_mtime))
        RESPONSE.setHeader('Content-Type', 'text/html')
        RESPONSE.setHeader('Content-Length', str(len(content)))
        RESPONSE.write(content)
        return ''

    security.declarePublic('getId')
    def getId(self):
        t = self.file.getId()
        if t.endswith('.raw'):
            t = t[:-len('.raw')]
        return t

    security.declareProtected(View, 'getParentNode')
    def getParentNode(self):
        # Needed by DICOD breadcrumb.
        return aq_parent(aq_inner(self))

    security.declareProtected(View, 'getProperty')
    def getProperty(self, prop):
        # Needed by DICOD breadcrumb.
        return None

    security.declareProtected(View, 'title_or_id')
    def title_or_id(self):
        # Needed by DICOD breadcrumb.
        return self.getId()

    security.declareProtected(View, 'absolute_url')
    def absolute_url(self, relative=0):
        # Needed by DICOD breadcrumb.
        u = self.getParentNode().absolute_url(relative=relative)
        u += '/'+self.getId()
        return u

InitializeClass(FileEncapsulator)


class EncapsulationFolderMixin(ExtensionClass.Base):
    """Mixin for folder that encapsulate its .html sub document."""

    def __getitem__(self, name):
        """Publishing traversal hook.

        Treats .html and .html.raw documents specially.

        .html documents call archivefolder_wrap to render.
        .html.raw documents are the original .html document.
        """
        try:
            ob = getattr(self, name)
        except AttributeError:
            pass
        else:
            return ob
        # Special encapsulation treatment.
        if not name.endswith('.html'):
            raise KeyError(name)
        raw_name = name+'.raw'
        # Get raw
        try:
            ob =  getattr(self, raw_name)
        except AttributeError:
            raise KeyError(raw_name)
        # DICOD: Put in place by ProxyBase during getitem traverse...
        context = getattr(self.REQUEST, 'cps_context', self)
        return FileEncapsulator(ob, context).__of__(self)

InitializeClass(EncapsulationFolderMixin)


class EncapsulationFolder(EncapsulationFolderMixin, Folder):
    """Folder that does encapsulation of subobjects."""
    meta_type = 'EncapsulationFolder'

    def __init__(self, id):
        self.id = id

    security = ClassSecurityInfo()
    security.declareObjectProtected(View)

InitializeClass(EncapsulationFolder)


class ArchiveFolderMixin(EncapsulationFolderMixin):
    """
    Archive (ZIP) folder
    """
    security = ClassSecurityInfo()

    _file = None
    _file_subids = ()

    security.declareProtected(ModifyPortalContent, 'editZip')
    def editZip(self, zip_file=None, zip_file_change=None):
        """Edit the object properties."""
        if zip_file_change in ('change', None):
            if zip_file is not None:
                self._updateZip(zip_file)
        elif zip_file_change == 'delete':
            self._clearZip()

    def _clearZip(self):
        """Remove contained zipfile object."""
        self._file = None
        self.manage_delObjects(list(self._file_subids))
        self._file_subids = ()

    def _updateZip(self, file):
        """Update content from zip file."""
        if not file:
            return
        self._clearZip()
        self._file = File('zipdata', '', file=file)
        zipfile = ZipFile(StringIO(str(self._file)))
        infolist = zipfile.infolist()
        for info in infolist:
            path = info.filename
            # Skip folders
            if path[-1] == '/':
                continue
            data = zipfile.read(path)
            self._installZip(path, data)

    def _installZip(self, path, data):
        """Install object (file) <path> with content <data>."""
        l = path.split("/")
        folder = self
        for id in l[0:-1]:
            if not hasattr(folder, id):
                subfolder = EncapsulationFolder(id)
                folder._setObject(id, subfolder)
                if folder is self:
                    self._file_subids += (id,)
            folder = getattr(folder, id)
        id = l[-1]
        # Store .html as .html.raw
        if id.endswith('.html'):
            id += '.raw'
        file = File(id, '', file=data)
        folder._setObject(id, file)
        if folder is self:
            self._file_subids += (id,)

InitializeClass(ArchiveFolderMixin)


class CPSArchiveFolder(ArchiveFolderMixin, CPSBaseDocument, Folder):
    """
    Archive (ZIP) folder
    """
    meta_type = 'CPSArchiveFolder'
    portal_type = 'CPSArchiveFolder'

    security = ClassSecurityInfo()

    def __init__(self, id, file='', **kw):
        """Constructor"""
        self._updateZip(file)
        CPSBaseDocument.__init__(self, id, **kw)

    security.declareProtected(ModifyPortalContent, 'edit')
    def edit(self, zip_file=None, zip_file_change=None, **kw):
        """Edit the object properties."""
        self.editZip(zip_file=zip_file, zip_file_change=zip_file_change)
        CPSBaseDocument.edit(self, **kw)

InitializeClass(CPSArchiveFolder)


def addCPSArchiveFolder(self, id, **kw):
    """
    Add an Archive Folder
    """
    obj = CPSArchiveFolder(id, **kw)
    CPSBase_adder(self, obj)
