from Testing import ZopeTestCase
from Products.CPSDefault.tests import CPSTestCase
ZopeTestCase.installProduct("CPSArchiveFolder")

CPSTestCase.setupPortal()

CPSArchiveFolderTestCase = CPSTestCase.CPSTestCase

