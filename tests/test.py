# TODO: 
# - don't depend on getDocumentSchemas / getDocumentTypes but is there
#   an API for that ?

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from Testing import ZopeTestCase
import CPSArchiveFolderTestCase

from Products.CPSArchiveFolder import ArchiveFolder


class Test(CPSArchiveFolderTestCase.CPSArchiveFolderTestCase):
    def afterSetUp(self):
        self.login('root')
        self.ws = self.portal.workspaces

    def beforeTearDown(self):
        self.logout()

    def testSimpleInstanciation(self):
        obj = ArchiveFolder.CPSArchiveFolder('af')
        self.portal._setObject('af', obj)

    def testInstanciationUsingZopeDispatcher(self):
        dispatcher = self.ws.manage_addProduct['CPSArchiveFolder']
        obj = dispatcher.addCPSArchiveFolder('af')

    def testSubObjects(self):
        obj = ArchiveFolder.CPSArchiveFolder('af', file=open("test.zip"))
        ids = obj.objectIds()
        self.assert_("coverage.py" in ids)
        self.assert_(len(obj.objectValues()) > 0)
        self.assert_(len(obj.objectItems()) > 0)

        file = obj['coverage.py']
        self.assert_(file.meta_type == "File")


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test))
    return suite

