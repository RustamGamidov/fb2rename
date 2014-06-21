#!/usr/bin/env python2
# -*- coding: UTF-8 -*-

import os
import argparse

from lxml import etree

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

format_patterns = [
    'author', 'title', 'date', 'seq_name', 'seq_number', 'genre',
    'oldname'
]


class XmlWrapper(object):

    @staticmethod
    def get_xmlns_tag_path(a_element, a_path):
        xmlns = a_element.nsmap[None]
        tags = []
        for tag in a_path.split('/'):
            tags.append('{' + xmlns + '}' + tag)
        return '/'.join(tags)

    @staticmethod
    def get_multitag_by_path(a_element, a_path):
        return a_element.findall(
            XmlWrapper.get_xmlns_tag_path(a_element, a_path)
        )

    @staticmethod
    def get_tag_by_path(a_element, a_path):
        return a_element.find(XmlWrapper.get_xmlns_tag_path(a_element, a_path))

    @staticmethod
    def get_multitag_values(a_element, a_path):
        tags = XmlWrapper.get_multitag_by_path(a_element, a_path)
        if len(tags) == 0:
            raise Exception("There's no " + a_path)
            return ['']
        values = []
        for tag in tags:
            cval = tag.text
            if cval is None:
                cval = ''
            values.append(cval)
        return values

    @staticmethod
    def get_tag_value(a_element, a_path):
        values = XmlWrapper.get_multitag_values(a_element, a_path)
        if len(values) > 0:
            return values[0]
        return []


def ensure_path_exists(path):
    if path:
        if not os.path.exists(path):
            os.makedirs(path)


replace_single_quote = ['"', u"\u00BB", u"\u00AB"]
replace_underscore = [u'…']
replace_dash = [u"–"]


def replace(i_str, i_forbidden, i_char):
    result = i_str.strip()
    for ch in i_forbidden:
        result = result.replace(ch, i_char)
    return result


def validate_common(i_str):
    result = i_str.strip()
    result = replace(result, [u'№'], 'n')
    result = replace(result, replace_single_quote, "'")
    result = replace(result, replace_underscore, "_")
    result = replace(result, replace_dash, "-")
    result = ' '.join(result.split())
    return result


def validate_filename(i_filename):
    result = validate_common(i_filename)
    result = replace(result, ['?', ':'], '.')
    return result


def validate_tag(i_tag):
    result = validate_common(i_tag)
    result = replace(result, ['\\', '/'], '.')
    return result


def get_tag_atribute(_element, _path, _attr):
    tag = XmlWrapper.get_tag_by_path(_element, _path)
    if tag is None:
        raise Exception("There's no " + _path + " " + _attr)
        return ''
    return tag.get(_attr)


def get_person_name(_element):
    try:
        fname = XmlWrapper.get_tag_value(_element, 'first-name')
    except:
        fname = ''
    try:
        lname = XmlWrapper.get_tag_value(_element, 'last-name')
    except:
        lname = ''
    try:
        mname = XmlWrapper.get_tag_value(_element, 'middle-name')
    except:
        mname = ''
    if not fname and not lname and not mname:
        raise Exception("There's no author")
        return ''
    result = ', '.join([lname, ' '.join([fname, mname])])
    return result


def get_author(_element):
    authors_tag = XmlWrapper.get_multitag_by_path(
        _element, title_tags['author'])
    if not authors_tag:
        raise Exception("There's no author")
        return ''
    authors = []
    for tag in authors_tag:
        author = get_person_name(tag)
        if author is not None:
            authors.append(author)
    return '. '.join(authors)


def get_sequence(_element):
    name = get_tag_atribute(_element, title_tags['sequence'], 'name')
    num = get_tag_atribute(_element, title_tags['sequence'], 'number')
    return '-'.join([name, num])


def get_simple_value(_element, _cmd_parameter):
    value = ' '
    if _cmd_parameter in title_tags.keys():
        value = XmlWrapper.get_tag_value(
            _element, title_tags[_cmd_parameter])
    elif _cmd_parameter in document_tags.keys():
        value = XmlWrapper.get_tag_value(
            _element, document_tags[_cmd_parameter])
    elif _cmd_parameter in publish_tags.keys():
        value = XmlWrapper.get_tag_value(
            _element, publish_tags[_cmd_parameter])

    if value is None:
        raise Exception("There's no " + _cmd_parameter)
        value = ''
    return validate_tag(value)


def get_combined_value(_element, _cmd_parameter, _oldname=''):
    value = ' '
    if _cmd_parameter == 'author':
        value = get_author(_element)
    elif _cmd_parameter == 'seq_name':
        value = get_tag_atribute(_element, title_tags['sequence'], 'name')
    elif _cmd_parameter == 'seq_number':
        value = get_tag_atribute(_element, title_tags['sequence'], 'number')
    elif _cmd_parameter == 'oldname':
        value = _oldname

    if value is None:
        raise Exception("There's no " + _cmd_parameter)
        value = ''
    return validate_tag(value)


def format_name(_fname, _format):
    book = etree.parse(_fname)
    element = book.getroot()
    result = _format
    oldfname = os.path.basename(os.path.splitext(_fname)[0])
    for ptrn in format_patterns:
        if ptrn in _format:
            value = get_combined_value(element, ptrn, oldfname)
            if value in [None, '']:
                value = get_simple_value(element, ptrn)
            if value is not None:
                result = result.replace('%' + ptrn + '%', value)
    return result


def main():
    parser = argparse.ArgumentParser(
        description='Renames given single fb2 file using pattern.')
    parser.add_argument(
        'fname', metavar='fb2_file_names', type=str, nargs='+',
        help='name of the files to rename')
    parser.add_argument(
        '--format', '-f', dest='format', action='store',
        default='%title%',
        help='Format of the new name')
    parser.add_argument(
        '--dry-run', '-d', dest='dryrun', action='store_true',
        default=False,
        help='Do not rename files. Just show new names.')
    args = parser.parse_args()

    errors = []
    for fname in args.fname:
        try:
            name = format_name(fname, args.format)
            name = unicode(validate_filename(name + '.fb2'))
        except:
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


if __name__ == '__main__':
    main()
