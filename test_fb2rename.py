#!/usr/bin/env python2
# -*- coding: UTF-8 -*-

import unittest
import shutil
import os
import sys
import tempfile
from fb2rename import *


def get_files(a_path=os.getcwd(), a_abspath=True):
    lsdir = os.listdir(a_path)
    lsdir = [f for f in lsdir if os.path.isfile(f)]
    if a_abspath:
        lsdir = [os.path.abspath(f) for f in lsdir]
    return lsdir


class CommonTest(unittest.TestCase):
    str_ch = r"lineOnlyWithCharachters"
    str_chNums = r"0line2Only7WithChara3456chters0"
    str_chUndr = r"_line_Only_WithChara____chters_"
    str_chSymb = r"&line%Only#WithChara4(&;chters)"


    @classmethod
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix=os.path.basename(__file__))
        os.chdir(self.tmpdir)


    @classmethod
    def tearDown(self):
        if os.path.exists(self.tmpdir):
            shutil.rmtree(self.tmpdir)


    def test_ensurePathExists_createsAskedPath(self):
        path2check = os.path.join(self.tmpdir, 'dir1', 'dir2', 'dir3')
        self.assertFalse(os.path.exists(path2check))
        Common.ensure_path_exists(path2check)
        self.assertTrue(os.path.exists(path2check))


    def test_ensurePathExists_doesNotThrow_whenPathExists(self):
        path2check = os.path.join(self.tmpdir, 'dir1', 'dir2', 'dir3')
        Common.ensure_path_exists(path2check)
        self.assertTrue(os.path.exists(path2check))
        msg = ''
        try:
            Common.ensure_path_exists(path2check)
        except:
            self.assertTrue(False, sys.exc_info()[0])


    def test_ensurePathExists_throws_whenPathIsNone(self):
        self.assertRaises(Exception, Common.ensure_path_exists, None)


    def test_ensurePathExists_doesNotThrow_whenPathIsEmpty(self):
        try:
            Common.ensure_path_exists('')
            Common.ensure_path_exists(u'')
        except:
            self.assertTrue(False, sys.exc_info()[0])


    def test_ensurePathExists_doesNotThrow_whenPathIsWhitespace(self):
        try:
            Common.ensure_path_exists(' ')
            Common.ensure_path_exists(u' ')
        except:
            self.assertTrue(False, sys.exc_info()[0])


    def test_ensurePathExists_throws_whenPathIsNotString(self):
        self.assertRaises(Exception, Common.ensure_path_exists, 17)
        self.assertRaises(Exception, Common.ensure_path_exists, ['e', 'werw'])


    def test_replace_returnsSameLine_whenAskedCharsAreEmpty(self):
        str_result = Common.replace(self.str_ch, '', '_')
        self.assertEqual(self.str_ch, str_result)


    def test_replace_returnsSameLine_whenAskedCharsAreNotPresent(self):
        str_result = Common.replace(self.str_ch, '!^%$', '_')
        self.assertEqual(self.str_ch, str_result)


    def test_replace_returnedStrippedLine_whenForbiddenCharsAreEmpty(self):
        str_to_check = ' \t  ' + self.str_ch + '   \t'
        str_result = Common.replace(str_to_check, '', '')
        self.assertEqual(self.str_ch, str_result)


    def test_replace_returnedStrippedLine_whenForbiddenCharsAreNotEmpty(self):
        str_to_check = ' \t  ' + self.str_chUndr + '   \t'
        str_result = Common.replace(str_to_check, '_', '')
        self.assertEqual(self.str_ch, str_result)


    def test_replace_replaceAnyAskedCharWithTheGivenOne_whenAskedCharsArePresent(self):
        str_forbidden = '&()#4;%'
        str_result = Common.replace(self.str_chSymb, str_forbidden, '_')
        self.assertEqual(self.str_chUndr, str_result)


    def test_getTemplates_returnsDictWithDefaultKey(self):
        self.assertTrue('default' in Common.get_templates())


class GetFilesToWorkWith(unittest.TestCase):
    dir_not_exists = 'not_exists'
    ref = {}

    @classmethod
    def setUpClass(self):
        def create_files(a_path):
            open(os.path.join(a_path, 'file1.fb2'), 'a').close()
            open(os.path.join(a_path, 'file2.fb2'), 'a').close()
            open(os.path.join(a_path, 'file3.fb2.zip'), 'a').close()
            open(os.path.join(a_path, 'file4.rar'), 'a').close()
            open(os.path.join(a_path, 'file5.zip'), 'a').close()
            open(os.path.join(a_path, 'file6.txt'), 'a').close()
            open(os.path.join(a_path, 'file7.avi'), 'a').close()

        def create_refs():
            self.ref['fb2_flat_root'] = [os.path.join(self.tmpdir, 'file1.fb2'), os.path.join(self.tmpdir, 'file2.fb2')]
            self.ref['fb2rar_flat_root'] = [os.path.join(self.tmpdir, 'file1.fb2'), os.path.join(self.tmpdir, 'file2.fb2'), os.path.join(self.tmpdir, 'file4.rar')]
            self.ref['fb2fb2zip_flat_root'] = [os.path.join(self.tmpdir, 'file1.fb2'), os.path.join(self.tmpdir, 'file2.fb2'), os.path.join(self.tmpdir, 'file3.fb2.zip')]

        self.tmpdir = tempfile.mkdtemp(prefix=os.path.basename(__file__))
        create_files(self.tmpdir)
        os.mkdir(os.path.join(self.tmpdir, 'dir1'))
        create_files(os.path.join(self.tmpdir, 'dir1'))
        os.mkdir(os.path.join(self.tmpdir, 'dir2'))
        create_files(os.path.join(self.tmpdir, 'dir2'))
        os.chdir(self.tmpdir)
        create_refs()


    @classmethod
    def tearDownClass(self):
        if os.path.exists(self.tmpdir):
            shutil.rmtree(self.tmpdir)


    def test_returnEmptyList_whenArgumentsAreDefault(self):
        files = get_files_to_work_with()
        self.assertEqual(0, len(files))


    def test_returnsEmptyList_whenTypesArgumentIsEmpty(self):
        files = get_files_to_work_with(get_files(), [], self.tmpdir)
        self.assertEqual(0, len(files))


    def test_returnsEmptyList_whenTypesArgumentIsNone(self):
        files = get_files_to_work_with(get_files(), None, self.tmpdir)
        self.assertEqual(0, len(files))


    def test_returnsEmptyList_whenTypesArgumentIsNotList(self):
        files = get_files_to_work_with(get_files(), 'not_list', self.tmpdir)
        self.assertEqual(0, len(files))


    def test_returnEmptyList_whenPathArgumentIsNotDir(self):
        files = get_files_to_work_with(get_files(), ['fb2', 'fb2.zip'], self.dir_not_exists)
        self.assertEqual(0, len(files))


    def test_returnEmptyList_whenPathArgumentIsNone(self):
        files = get_files_to_work_with(get_files(), ['fb2', 'fb2.zip'], None)
        self.assertEqual(0, len(files))


    def test_returnProperValues_whenTypesArgumentContainsOneItem(self):
        files = get_files_to_work_with(get_files(os.getcwd()), ['fb2'], self.tmpdir)
        self.assertEqual(sorted(self.ref['fb2_flat_root']), sorted(files))


    def test_returnProperValues_whenTypesArgumentContainsExistingTypes(self):
        files = get_files_to_work_with(get_files(os.getcwd()), ['fb2', 'rar'], self.tmpdir)
        self.assertEqual(sorted(self.ref['fb2rar_flat_root']), sorted(files))


    def test_returnProperValues_whenTypesArgumentContainsDoubledExtension(self):
        files = get_files_to_work_with(get_files(os.getcwd()), ['fb2', 'fb2.zip'], self.tmpdir)
        self.assertEqual(sorted(self.ref['fb2fb2zip_flat_root']), sorted(files))


if __name__ == '__main__':
    unittest.main()
