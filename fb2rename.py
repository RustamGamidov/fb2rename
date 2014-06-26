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
    'author', 'title', 'date', 'sequence', 'seq_name', 'seq_number', 'genre',
    'oldname'
]


class Common(object):
    replace_single_quote = ['"', u"\u00BB", u"\u00AB"]
    replace_underscore = [u'…']
    replace_dash = [u"–"]

    @staticmethod
    def ensure_path_exists(path):
        if path:
            if not os.path.exists(path):
                os.makedirs(path)

    @staticmethod
    def replace(a_str, a_forbidden, a_char):
        result = a_str.strip()
        for ch in a_forbidden:
            result = result.replace(ch, a_char)
        return result

    @staticmethod
    def validate_common(a_str):
        result = a_str.strip()
        result = Common.replace(result, [u'№'], 'n')
        result = Common.replace(result, Common.replace_single_quote, "'")
        result = Common.replace(result, Common.replace_underscore, "_")
        result = Common.replace(result, Common.replace_dash, "-")
        result = ' '.join(result.split())
        return result

    @staticmethod
    def validate_filename(a_filename):
        result = Common.validate_common(a_filename)
        result = Common.replace(result, ['?', ':'], '.')
        return result

    @staticmethod
    def validate_tag(a_tag):
        result = Common.validate_common(a_tag)
        result = Common.replace(result, ['\\', '/'], '.')
        return result


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

    @staticmethod
    def get_tag_atribute(a_element, a_path, a_attr):
        tag = XmlWrapper.get_tag_by_path(a_element, a_path)
        if tag is None:
            raise Exception("There's no " + a_path + " " + a_attr)
            return ''
        return tag.get(a_attr)

    @staticmethod
    def get_all_tag_atributes(a_element, a_path):
        tag = XmlWrapper.get_tag_by_path(a_element, a_path)
        if tag is None:
            raise Exception("There's no " + a_path)
            return {}
        return tag.attrib


class Book(object):
    def __init__(self):
        self.items = [
            'oldname', 'authors', 'genres',
            'title', 'year', 'date',
            'sequnce', 'seq_name', 'seq_number'
        ]
        self.lst_items = [
            'authors', 'genres'
        ]
        self.filepath = ''
        self.format = ''

    @staticmethod
    def format_person_name(a_first, a_middle, a_last):
        if not a_first and not a_last and not a_middle:
            raise Exception("There's no author")
        result = ', '.join([a_last, ' '.join([a_first, a_middle])])
        return result

    def open_virtual(self, a_path):
        raise NotImplementedError('virtual function')

    def open(self, a_path):
        if not os.path.exists(a_path):
            return
        self.filepath = a_path
        self.open_virtual(a_path)

    def get_value_virtual(self, a_item):
        raise NotImplementedError('virtual function')

    def get_value(self, a_item):
        if a_item in self.items:
            return self.get_value_virtual(a_item)
        return []

    def get_oldname(self):
        if self.filepath:
            return os.path.splittext(os.path.basename(self.filepath))[0]
        return ''


class Book_fb2(Book):
    def __init__(self):
        super(Book_fb2, self).__init__()
        self.format = 'fb2'
        self.tags_path = {
            'title':    'description/title-info/book-title',
            'authosr':  'description/title-info/author'
        }

    def open_virtual(self, a_path):
        self.book = etree.parse(a_path).getroot()
        self.xmlns = self.book.nsmap[None]
        pass

    def get_value_virtual(self, a_item):
        if(a_item == 'oldname'):
            return self.get_oldname()
        return ''

    def get_tag_value(self, a_tag_path):
        return


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
    return Book.format_person_name(fname, mname, lname)


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
    attrs = XmlWrapper.get_all_tag_atributes(_element, title_tags['sequence'])
    name = ''
    if 'name' in attrs.keys():
        name = attrs['name']
    num = ''
    if 'number' in attrs.keys():
        num = attrs['number']
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
    return Common.validate_tag(value)


def get_combined_value(_element, _cmd_parameter, _oldname=''):
    value = ' '
    if _cmd_parameter == 'author':
        value = get_author(_element)
    elif _cmd_parameter == 'sequence':
        value = get_sequence(_element)
    elif _cmd_parameter == 'seq_name':
        value = XmlWrapper.get_tag_atribute(
            _element, title_tags['sequence'], 'name')
    elif _cmd_parameter == 'seq_number':
        value = XmlWrapper.get_tag_atribute(
            _element, title_tags['sequence'], 'number')
    elif _cmd_parameter == 'oldname':
        value = _oldname

    if value is None:
        raise Exception("There's no " + _cmd_parameter)
        value = ''
    return Common.validate_tag(value)


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
            name = unicode(Common.validate_filename(name + '.fb2'))
        except:
            errors.append(fname)
            continue
        name = name.strip('\n ')
        print fname, ' => ', name
        if not args.dryrun:
            try:
                Common.ensure_path_exists(os.path.dirname(name))
                os.rename(fname, name)
            except:
                errors.append(fname)

    print 'Errors: ', errors


if __name__ == '__main__':
    main()
