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
     ManageProperties, ChangePermissions
from Products.CPSCore.CPSBase import CPSBaseDocument, CPSBase_adder
from OFS.Image import File
from zLOG import LOG, DEBUG
from StringIO import StringIO
from types import StringType
from zipfile import ZipFile

_marker = []

# FIXME: fix this with actual information
factory_type_information = ({ 
    'id': 'CPSArchiveFolder',
    'meta_type': 'CPSArchiveFolder',
    'description': "portal_type_ArchiveFolder_description",
    'icon': '',
    'title': "portal_type_ArchiveFolder_title",
    'product': 'CPSArchiveFolder',
    'factory': 'addCPSArchiveFolder',
    'immediate_view': 'xxx',
    'allow_discussion': 0,
    'actions': ({
        'id': 'view',
        'name': 'action_view',
        'action': 'archivefolder_view',
        'permissions': (View,),
    }, {
        'id': 'create',
        'name': 'action_create',
        'action': 'forum_create_form',
        'visible': 0,
        'permissions': ('',)
    }, {
        'id': 'edit',
        'name': 'action_modify',
        'action': 'forum_edit_form',
        'permissions': (ManageProperties,),
    }, {
        'id': 'localroles',
        'name': 'action_local_roles',
        'action': 'folder_localrole_form',
        'permissions': (ChangePermissions,),
    }, {
        'id': 'isfunctionalobject',
        'name': 'isfunctionalobject',
        'action': 'isfunctionalobject',
        'visible': 0,
        'permissions': ('',),
    }, {
        'id': 'isproxytype',
        'name': 'isproxytype',
        'action': 'document',
        'visible': 0,
        'permissions': ('',),
    }, {
        'id': 'issearchabledocument',
        'name': 'issearchabledocument',
        'action': 'issearchabledocument',
        'visible': 0,
        'permissions': ('',),
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
    allow_discussion = 1
    security = ClassSecurityInfo()

    _file = None
    _object_ids = ()

    def __init__(self, id, file='', **kw):
        """Constructor"""
        self._update(file)
        CPSBaseDocument.__init__(self, id, **kw)

    def _update(self, file):
        if not file:
            return

        if type(file) == StringType:
            self._file = file
        else:
            self._file = file.read()
        zf = ZipFile(StringIO(self._file))
        infolist = zf.infolist()
        ids = []
        for info in infolist:
            if not info.filename.count('/'):
                ids.append(info.filename)
        self._object_ids = tuple(ids)

    # XXX: how do we use this ?
    #def __bobo_traverse__(self, REQUEST, id):
    #    try:
    #        return self._getOb(id)
    #    except 'NotFound':
    #        return getattr(self, id)

    def __getitem__(self, id):
        return self._getOb(id)

    def objectIds(self, spec=None):
        return self._object_ids

    def objectValues(self, spec=None):
        return [ self._getOb(id) for id in self._object_ids ]

    def objectItems(self, spec=None):
        return [ (id, self._getOb(id)) for id in self._object_ids ]

    def _getOb(self, id, default=_marker):
        # XXX: what about 'default'?
        if self._file:
            zf = ZipFile(StringIO(self._file))
            data = zf.read(id)
            return File(id, '', data).__of__(self)
        else:
            raise 'NotFound' # XXX: check if this is the right exception

