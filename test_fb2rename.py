#!/usr/bin/env python2
# -*- coding: UTF-8 -*-

import unittest
import shutil
import os
import sys
from fb2rename import *


global_test_workspace = '/tmp/fb2rename_test_workspace'


class CommonTest(unittest.TestCase):
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


    def test_replace_returnsSameLine_whenAskedCharsAreNotPresent(self):
        str_to_check = 'lineFlineZanother23sadfF'
        str_result = Common.replace(str_to_check, '!^%$', '_')
        self.assertEqual(str_to_check, str_result)


    def test_replace_returnedStrippedLine(self):
        str_to_check = ' asd asa '
        str_reference = 'asd asa'
        str_result = Common.replace(str_to_check, '', '')
        self.assertEqual(str_reference, str_result)


    def test_replace_replaceAnyAskedCharWithTheGivenOne_whenAskedCharsArePresent(self):
        str_to_check = 'lineFlineZanother23sadfF'
        str_reference = 'line_line_another_3sadf_'
        str_forbidden = 'FZ2'
        char_to_insert = '_'
        str_result = Common.replace(str_to_check, str_forbidden, char_to_insert)
        self.assertEqual(str_result, str_reference)


if __name__ == '__main__':
    unittest.main()
