#!/usr/bin/env python2
# -*- coding: UTF-8 -*-

import os
import glob
import sys
import fnmatch
import argparse
import string

from lxml import etree

#import xml.dom.minidom
#from xml.dom.minidom import Node


title_tags = {
'genre': 'description/title-info/genre',
'author': 'description/title-info/author',
'author_fname': 'description/title-info/author/first-name',
'author_mname': 'description/title-info/author/middle-name',
'author_lname': 'description/title-info/author/last-name',
'author_id': 'description/title-info/author/id',
'title': 'description/title-info/book-title',
'date': 'description/title-info/date',
'lang': 'description/title-info/lang',
'lang_src': 'description/title-info/src-lang',
'sequence': 'description/title-info/sequence'
}

document_tags = {
'author': 'description/document-info/author',
'date': 'description/document-info/date',
'version': 'description/document-info/version',
'publisher': 'description/document-info/publisher'
}

publish_tags = {
'bookname': 'description/publish-info/bookname',
'publisher': 'description/publish-info/publisher',
'city': 'description/publish-info/city',
'year': 'description/publish-info/year',
'isbn': 'description/publish-info/isbn',
'sequence': 'description/publish-info/sequence'
}

format_patterns = ['author', 'title', 'date', 'seq_name', 'seq_number', 'genre']

def ensure_path_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)


def validate_filename(i_filename):
    forbidden = ['?', ':']
    result = i_filename.strip()
    for ch in forbidden:
        result = result.replace(ch,'.')
    return result


def validate_tag(i_tag):
    forbidden = ['\\', '/', '"']
    result = i_tag.strip()
    result = validate_filename(result)
    result = ' '.join(result.split())
    for ch in forbidden:
        result = result.replace(ch,'_')
    return result


def get_tag_path(_element, _path):
    xmlns = _element.nsmap[None]
    tags = []
    for tag in _path.split('/'):
        tags.append('{' + xmlns + '}' + tag)
    return _element.find('/'.join(tags))


def get_tag_value(_element, _path):
    tag = get_tag_path(_element, _path)
    if tag is None:
        raise Exception("There's no " + _path)
        return ''
    value = tag.text
    if value is None:
        value = ''
    return value


def get_tag_atribute(_element, _path, _attr):
    tag = get_tag_path(_element, _path)
    if tag is None:
        raise Exception("There's no " + _path + " " + _attr)
        return ''
    return tag.get(_attr)


def get_author(_element):
    author = get_tag_value(_element, title_tags['author'])
    if author is None:
        raise Exception("There's no author")
        return ''
    try:
        fname = get_tag_value(_element, title_tags['author_fname'])
    except:
        fname = ''
    try:
        lname = get_tag_value(_element, title_tags['author_lname'])
    except:
        lname = ''
    try:
        mname = get_tag_value(_element, title_tags['author_mname'])
    except:
        mname = ''
    if not fname and not lname and not mname:
        raise Exception("There's no author")
        return ''
    author = ', '.join([lname, ' '.join([fname, mname])])
    return author


def get_sequence(_element):
    name = get_tag_atribute(_element, title_tags['sequence'], 'name')
    num = get_tag_atribute(_element, title_tags['sequence'], 'number')
    return '-'.join([name, num])


def get_cmd(_element, _cmd_parameter):
    """returns fb2 value corresponding to the placeholder"""
    value = ' '
    if _cmd_parameter == 'author':
        value = get_author(_element)
    elif _cmd_parameter == 'seq_name':
        value = get_tag_atribute(_element, title_tags['sequence'], 'name')
    elif _cmd_parameter == 'seq_number':
        value = get_tag_atribute(_element, title_tags['sequence'], 'number')
    elif _cmd_parameter in title_tags.keys():
        value = get_tag_value(_element, title_tags[_cmd_parameter])
    elif _cmd_parameter in document_tags.keys():
        value = get_tag_value(_element, document_tags[_cmd_parameter])
    elif _cmd_parameter in publish_tags.keys():
        value = get_tag_value(_element, publish_tags[_cmd_parameter])
    if value is None:
        raise Exception("There's no " + _cmd_parameter)
        value = ''
    return validate_tag(value)


def format_name(_element, _format):
    result = _format
    for ptrn in format_patterns:
        if ptrn in _format:
            value = get_cmd(_element, ptrn)
            if value is not None:
                result = result.replace('%' + ptrn + '%', value)
    return result


parser = argparse.ArgumentParser(description='Renames given single fb2 file using pattern.')
parser.add_argument('fname', metavar='fb2_file_names', type=str, nargs='+',
                   help='name of the files to rename')
parser.add_argument('--format', '-f', dest='format', action='store',
                   default='%title%',
                   help='Format of the new name')
parser.add_argument('--dry-run', '-d', dest='dryrun', action='store_true',
                   default=False,
                   help='Do not rename files. Just show new names.')
args = parser.parse_args()

errors = []
for fname in args.fname:
    book = etree.parse(fname)
    try:
        name = unicode(validate_filename(format_name(book.getroot(), args.format)) + '.fb2')
    except:
        print sys.exc_info()[1]
        errors.append(fname)
        continue
    name = name.strip('\n ')
    print fname, ' => ', name
    if not args.dryrun:
        try:
            ensure_path_exists(os.path.dirname(name))
            os.rename(fname, name)
        except:
            errors.append(fname)

print 'Errors: ', errors
