from Testing import ZopeTestCase
from Products.CPSDefault.Installer import BaseInstaller
from Products.CPSDefault.tests import CPSTestCase
ZopeTestCase.installProduct("CPSArchiveFolder")

CPSTestCase.setupPortal()

class CPSArchiveFolderInstaller(BaseInstaller):
    product_name = 'CPSArchiveFolder'

SKINS = (
    ("cps_archive_folder", 
        "Products/CPSArchiveFolder/skins/cps_archive_folder"),
)

class CPSArchiveFolderTestCase(CPSTestCase.CPSTestCase):
    def setUp(self):
        CPSTestCase.CPSTestCase.setUp(self)
        cmfcore_factory = self.portal.portal_skins.manage_addProduct['CMFCore']

        installer = CPSArchiveFolderInstaller(self.portal)
        installer.setupSkins(SKINS)

