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
        dispatcher.addCPSArchiveFolder('af')
        self.assert_(self.ws.af)

    def testSubObjects(self):
        dispatcher = self.ws.manage_addProduct['CPSArchiveFolder']

        # XXX: doesn't work ! Why ?
        # dispatcher.addCPSArchiveFolder('af', file=open("test.zip"))

        dispatcher.addCPSArchiveFolder('af')
        obj = self.ws.af
        obj.edit(zip_file=open("test_flat.zip"))
        self.assert_(obj._file)

        ids = obj.objectIds()
        self.assert_("coverage.py" in ids)
        self.assert_("test.html.raw" in ids)
        self.assert_(obj["test.html"])
        self.assert_(len(obj.objectValues()) > 0)
        self.assert_(len(obj.objectItems()) > 0)

        file = obj['coverage.py']
        self.assertEquals(file.meta_type, 'File')
        self.assertEquals(file.content_type, 'text/x-python')

        file = obj['test.html']
        self.assertEquals(file.meta_type, 'FileEncapsulator')
        #self.assertEquals(file.content_type, 'text/html')

        #obj.REQUEST['PARENTS'] = [self.portal.aq_parent]
        #print obj.REQUEST.traverse("/portal/workspaces/af")

        self.assertEquals(obj._getOb("no such id", None), None)
        self.assertRaises(AttributeError, obj._getOb, "no such id")

        # Delete file
        obj.edit(zip_file=None, zip_file_change='delete')
        self.assertEquals(obj._file, None)
        self.assertEquals(len(obj.objectIds()), 0)
        self.assertRaises(AttributeError, obj._getOb, "no such id")
        self.assertEquals(obj._getOb("no such id", None), None)

        # Upload file again
        obj.edit(zip_file=open("test_flat.zip"))
        self.assert_(obj._file)
        self.assert_(len(obj.objectIds()))

    def testSkins(self):
        self.assert_(self.portal.archivefolder_edit)
        self.assert_(self.portal.archivefolder_edit_form)
        self.assert_(self.portal.archivefolder_view)
        self.assert_(self.portal.archivefolder_wrap_template)

    # After "nested ZIP" refactoring
    def testNested(self):
        dispatcher = self.ws.manage_addProduct['CPSArchiveFolder']
        dispatcher.addCPSArchiveFolder('af')
        af = self.ws.af
        af.edit(zip_file=open("test_nested.zip"))

        for path in "test.py CVS CVS/Root CVS/Repository CVS/Entries".split():
            assert af.unrestrictedTraverse(path)

        folder = af.CVS
        self.assertEquals(folder.meta_type, "EncapsulationFolder")

        file = af.CVS.Root
        self.assertEquals(file.meta_type, "File")
        self.assertEquals(
            file.index_html(file.REQUEST, file.REQUEST.RESPONSE).strip(), 
            ":ext:fermigier@cvs.in.nuxeo.com:/home/cvs")

        #self.portal.REQUEST['PARENTS'] = [self.portal.aq_parent]
        #ob = self.portal.REQUEST.traverse("/portal/workspaces/af/CVS/Root")
        #self.assertEquals(ob.aq_base, af.aq_base)
        #self.assertEquals(ob().index_html().strip(), 
        #                  ":ext:fermigier@cvs.in.nuxeo.com:/home/cvs")


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test))
    return suite

