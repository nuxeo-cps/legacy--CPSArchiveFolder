# (C) Copyright 2003 Nuxeo SARL <http://nuxeo.com>
# (C) Copyright 2003 Commissariat à l'Énergie Atomique <http://www.cea.fr/>
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

from Products.CMFCore import utils
from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore.CMFCorePermissions import AddPortalContent

import ArchiveFolder

contentClasses = ()
contentConstructors = ()
fti = ()

fti += ArchiveFolder.factory_type_information
contentClasses += (ArchiveFolder.CPSArchiveFolder,)
contentConstructors += (ArchiveFolder.addCPSArchiveFolder,)

registerDirectory('skins/cps_archive_folder', globals())

def initialize(registrar):
    utils.ContentInit('CPS Archive Folder',
        content_types=contentClasses,
        permission=AddPortalContent,
        extra_constructors=contentConstructors,
        fti=fti).initialize(registrar)

