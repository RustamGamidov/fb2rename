#!/usr/bin/env python2
# -*- coding: UTF-8 -*-

import unittest
import shutil
import os
import sys
from fb2rename import *


global_test_workspace = '/tmp/fb2rename_test_workspace'


class CommonTest(unittest.TestCase):
    str_ch = r"lineOnlyWithCharachters"
    str_chNums = r"0line2Only7WithChara3456chters0"
    str_chUndr = r"_line_Only_WithChara____chters_"
    str_chSymb = r"&line%Only#WithChara4(&;chters)"


    @classmethod
    def setUp(self):
        global global_test_workspace
        if global_test_workspace:
            if os.path.exists(global_test_workspace):
                shutil.rmtree(global_test_workspace)
            os.makedirs(global_test_workspace)
        self.old_dir = os.getcwd()
        os.chdir(global_test_workspace)


    @classmethod
    def tearDown(self):
        os.chdir(self.old_dir)
        global global_test_workspace
        if global_test_workspace:
            shutil.rmtree(global_test_workspace)


    def test_ensurePathExists_createsAskedPath(self):
        path2check = os.path.join(global_test_workspace, 'dir1', 'dir2', 'dir3')
        self.assertFalse(os.path.exists(path2check))
        Common.ensure_path_exists(path2check)
        self.assertTrue(os.path.exists(path2check))


    def test_ensurePathExists_doesNotThrow_whenPathExists(self):
        path2check = os.path.join(global_test_workspace, 'dir1', 'dir2', 'dir3')
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


if __name__ == '__main__':
    unittest.main()
