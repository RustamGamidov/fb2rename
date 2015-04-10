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

    def test_replace_replaceForbidenChars_whenAskedCharsArePresent(self):
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
        self.tmpdir = tempfile.mkdtemp(prefix=os.path.basename(__file__))
        ref_dirs = [
            self.tmpdir, os.path.join(self.tmpdir, 'dir1'),
            os.path.join(self.tmpdir, 'dir2')]
        files = self.get_ref(ref_dirs, [
            'fb2', 'fb2.zip', 'rar', 'zip', 'txt', 'avi'])
        for f in files:
            open(f, 'a').close()
        os.chdir(self.tmpdir)

    @classmethod
    def tearDownClass(self):
        if os.path.exists(self.tmpdir):
            shutil.rmtree(self.tmpdir)

    @classmethod
    def get_ref_files(self, a_types):
        result = []
        if 'fb2' in a_types:
            result.append('file1.fb2')
            result.append('file2.fb2')
        if 'fb2.zip' in a_types:
            result.append('file3.fb2.zip')
        if 'rar' in a_types:
            result.append('file4.rar')
        if 'zip' in a_types:
            result.append('file5.zip')
        if 'txt' in a_types:
            result.append('file6.txt')
        if 'avi' in a_types:
            result.append('file7.avi')
        return result

    @classmethod
    def get_ref(self, a_dirs, a_types):
        result = []
        files = self.get_ref_files(a_types)
        for d in a_dirs:
            if not os.path.exists(d):
                os.mkdir(d)
            result.extend([os.path.join(d, t) for t in files])
        return result

    def test_returnEmptyList_whenArgumentsAreDefault(self):
        files = get_files_to_work_with()
        self.assertEqual(0, len(files))

    def test_returnsEmptyList_whenTypesArgumentIsEmpty(self):
        files = get_files_to_work_with(get_files(), [], [self.tmpdir])
        self.assertEqual(0, len(files))

    def test_returnsEmptyList_whenTypesArgumentIsNone(self):
        files = get_files_to_work_with(get_files(), None, [self.tmpdir])
        self.assertEqual(0, len(files))

    def test_returnsEmptyList_whenTypesArgumentIsNotList(self):
        files = get_files_to_work_with(get_files(), 'not_list', [self.tmpdir])
        self.assertEqual(0, len(files))

    def test_returnEmptyList_whenPathArgumentIsNotDir(self):
        types = ['fb2', 'fb2.zip']
        path = [self.dir_not_exists]
        files = get_files_to_work_with(get_files(), types, path)
        self.assertEqual(0, len(files))

    def test_returnEmptyList_whenPathArgumentIsNone(self):
        files = get_files_to_work_with(get_files(), ['fb2', 'fb2.zip'], None)
        self.assertEqual(0, len(files))

    def test_returnProperValues_whenTypesArgumentContainsOneItem(self):
        types = ['fb2']
        path = [self.tmpdir]
        files = get_files_to_work_with(get_files(os.getcwd()), types, path)
        ref = self.get_ref([self.tmpdir], types)
        self.assertEqual(sorted(ref), sorted(files))

    def test_returnProperValues_whenTypesArgumentContainsExistingTypes(self):
        types = ['fb2', 'rar']
        path = [self.tmpdir]
        files = get_files_to_work_with(get_files(os.getcwd()), types, path)
        ref = self.get_ref([self.tmpdir], types)
        self.assertEqual(sorted(ref), sorted(files))

    def test_returnProperValues_whenTypesArgumentContainsDoubledExtension(self):
        types = ['fb2', 'fb2.zip']
        path = [self.tmpdir]
        files = get_files_to_work_with(get_files(os.getcwd()), types, path)
        ref = self.get_ref([self.tmpdir], types)
        self.assertEqual(sorted(ref), sorted(files))

    def test_returnProperValues_whenTypesArgumentContainsNotExistingExtension(self):
        types = ['fb2', 'ogg']
        path = [self.tmpdir]
        files = get_files_to_work_with(get_files(os.getcwd()), types, path)
        ref = self.get_ref([self.tmpdir], ['fb2'])
        self.assertEqual(sorted(ref), sorted(files))

    def test_getFilesFromTheArgumentPath_whenFilesArgumentIsEmpty(self):
        files = get_files_to_work_with([], ['fb2'], [self.tmpdir])
        ref = self.get_ref([self.tmpdir], ['fb2'])
        self.assertEqual(sorted(ref), sorted(files))

    def test_getFilesFromTheArgumentPath_whenFilesArgumentIsNotEmpty(self):
        dirs_to_scan = [os.path.join(self.tmpdir, 'dir1')]
        files = get_files_to_work_with(get_files(os.getcwd()), ['fb2'], dirs_to_scan)
        ref = self.get_ref([self.tmpdir], ['fb2'])
        ref.extend(self.get_ref(dirs_to_scan, ['fb2']))
        self.assertEqual(sorted(ref), sorted(files))


if __name__ == '__main__':
    unittest.main()
