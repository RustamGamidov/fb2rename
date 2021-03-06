#!/usr/bin/env python2
# -*- coding: UTF-8 -*-

import os
import argparse
import sys
import re
from time import strftime, strptime
from lxml import etree


class Common(object):
    replace_single_quote = ['"', u"\u00BB", u"\u00AB"]
    replace_underscore = [u'…']
    replace_dash = [u"–"]

    @staticmethod
    def ensure_path_exists(path):
        if not isinstance(path, str) and \
            not isinstance(path, unicode):
            raise TypeError
        path = os.path.realpath(path.strip())
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

    @staticmethod
    def get_templates():
        templates = {}
        templates['simple_flat']    = r'%title%'
        templates['flat']           = r'%authors% - %title%'
        templates['sequence']       = r'%seq_name%\%seq_number%. %title%'
        templates['sequence_flat']  = r'%seq_name% - %seq_number%. %title%'
        templates['default']        = templates['flat']
        return templates

    @staticmethod
    def get_format_patterns():
        return [
            'authors', 'title', 'date', 'sequence',
            'seq_name', 'seq_number', 'genre', 'oldname', 'year'
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
            'sequence', 'seq_name', 'seq_number'
        ]
        self.lst_items = [
            'authors', 'genres'
        ]
        self.filepath = ''
        self.format = ''

    @staticmethod
    def format_person_name(a_first, a_middle, a_last, a_format='#L, #F #M'):
        if not a_first and not a_last and not a_middle:
            raise Exception("There's no author")
        if not a_first: a_first = ' '
        if not a_middle: a_middle = ' '
        if not a_last: a_last = ' '
        result = a_format
        result = result.replace('#L', a_last)
        result = result.replace('#l', a_last[0])
        result = result.replace('#M', a_middle)
        result = result.replace('#m', a_middle[0])
        result = result.replace('#F', a_first)
        result = result.replace('#f', a_first[0])
        return result.strip()

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
        return self.get_value_virtual(a_item)

    def get_oldname(self):
        if self.filepath:
            return os.path.splitext(os.path.basename(self.filepath))[0]
        return ''


class Book_fb2(Book):
    title_tags = {
        'genre': 'description/title-info/genre',
        'authors': 'description/title-info/author',
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
        'authors': 'description/document-info/author',
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

    def __init__(self):
        super(Book_fb2, self).__init__()
        self.format = 'fb2'

    def open_virtual(self, a_path):
        self.book = etree.parse(a_path).getroot()
        self.xmlns = self.book.nsmap[None]
        pass

    @staticmethod
    def get_person_name(a_element, a_format):
        try:
            fname = XmlWrapper.get_tag_value(a_element, 'first-name')
        except:
            fname = ' '
        try:
            lname = XmlWrapper.get_tag_value(a_element, 'last-name')
        except:
            lname = ' '
        try:
            mname = XmlWrapper.get_tag_value(a_element, 'middle-name')
        except:
            mname = ' '
        return Book.format_person_name(fname, mname, lname, a_format)

    def get_authors(self, _format):
        author_format = _format.replace('authors', '').strip()
        if not author_format:
            author_format = '#L, #F #M'
        authors_tag = XmlWrapper.get_multitag_by_path(
            self.book, self.title_tags['authors'])
        if not authors_tag:
            raise Exception("There's no author")
            return ''
        authors = []
        for tag in authors_tag:
            author = self.get_person_name(tag, author_format)
            if author is not None:
                authors.append(author)
        return '; '.join(authors)

    def get_sequence(self):
        attrs = XmlWrapper.get_all_tag_atributes(
            self.book, self.title_tags['sequence'])
        name = ''
        if 'name' in attrs.keys():
            name = attrs['name']
        num = ''
        if 'number' in attrs.keys():
            num = attrs['number']
        return '-'.join([name, num])

    def get_date(self):
        attrs = XmlWrapper.get_all_tag_atributes(
            self.book, self.title_tags['date'])
        if not attrs:
            raise Exception("There's no date")
        val = ''
        if 'value' in attrs.keys():
            val = strptime(attrs['value'], "%Y-%m-%d")
        return val

    def get_value_virtual(self, a_item):
        value = ''
        if re.match('authors', a_item):
            value = self.get_authors(a_item)
        elif a_item == 'sequence':
            value = self.get_sequence()
        elif a_item == 'seq_name':
            value = XmlWrapper.get_tag_atribute(
                self.book, self.title_tags['sequence'], 'name')
        elif a_item == 'seq_number':
            value = XmlWrapper.get_tag_atribute(
                self.book, self.title_tags['sequence'], 'number')
        elif a_item == 'oldname':
            value = self.get_oldname()
        elif a_item == 'date':
            dt = self.get_date()
            value = strftime("%Y-%m-%d", dt)
        elif a_item == 'year':
            dt = self.get_date()
            value = strftime("%Y", dt)
        elif a_item in self.title_tags.keys():
            value = XmlWrapper.get_tag_value(
                self.book, self.title_tags[a_item])
        elif a_item in self.document_tags.keys():
            value = XmlWrapper.get_tag_value(
                self.book, self.document_tags[a_item])
        elif a_item in self.publish_tags.keys():
            value = XmlWrapper.get_tag_value(
                self.book, self.publish_tags[a_item])

        if value is None:
            raise Exception("There's no " + a_item)
            value = ''
        return Common.validate_tag(value)


def format_name(a_book, _format):
    result = _format
    for ptrn in Common.get_format_patterns():
        re_ptrn = '%' + ptrn + '.*?%'
        ptrn_found = re.search(re_ptrn, result)
        while ptrn_found:
            pf_str = ptrn_found.group(0)
            value = a_book.get_value(pf_str.replace('%', ''))
            result = re.sub(re_ptrn, value, result, 1)
            ptrn_found = re.search(re_ptrn, result)
    return result


def get_files_to_work_with(a_files=[], a_types=[], a_path=[], a_recursive=False):
    if not isinstance(a_types, list):
        return []
    if not isinstance(a_path, list):
        return []
    result = []
    candidates = []
    candidates.extend(a_files)

    def get_files_plain(a_dir):
        lsdir = []
        if os.path.isdir(a_dir):
            lsdir = os.listdir(a_dir)
            lsdir = [os.path.join(a_dir, i) for i in lsdir]
            lsdir = [f for f in lsdir if os.path.isfile(f)]
        return lsdir

    def get_files_recursive(a_dir):
        lsdir = []
        if os.path.isdir(a_dir):
            for f in content:
                curr_subdir_name = f[0]
                curr_subdir_files = f[2]
                for fc in curr_subdir_files:
                    lsdir.append(os.path.join(p, curr_subdir_name, fc))
        return lsdir

    if not candidates and not a_path:
        a_path.append(os.getcwd())
    for p in a_path:
        if os.path.isdir(p):
            content = os.walk(p)
            lsdir = []
            if a_recursive:
                lsdir = get_files_recursive(p)
            else:
                lsdir = get_files_plain(p)
            candidates.extend(lsdir)
    candidates = [os.path.abspath(f) for f in candidates]
    candidates = list(set(candidates))
    extensions = [('.' + ext) for ext in a_types]
    for f in candidates:
        if 0 < len([e for e in extensions if f.endswith(e)]):
            result.append(f)
    return result


def manage_cmd():
    parser = argparse.ArgumentParser(
        description='Renames given single fb2 file using pattern.')
    parser.add_argument(
        'fname', metavar='fb2_file_names', type=str, nargs='*',
        help='name of the files to rename')
    parser.add_argument(
        '--format', '-f', dest='format', action='store',
        help='Format of the new name. Possble values are: ' +
        ', '.join(Common.get_format_patterns()) + '.\n' +
        'Author name could be #F/M/L like #First/Middle/Last name.'
    )
    parser.add_argument(
        '--template', '-t', metavar='template', action='store',
        default='default',
        help='Predefined formats. Possble value are: ' +
        ', '.join(Common.get_templates()) + '.'
    )
    parser.add_argument(
        '--dry-run', '-d', dest='dryrun', action='store_true',
        default=False,
        help='Do not rename files. Just show new names.')
    parser.add_argument(
        '--recursive', '-r', dest='recursive', type=bool, action='store',
        default=False,
        help='Scan given directories recursively.'
    )
    parser.add_argument(
        '-o', dest='out_dir', action='store',
        default='',
        help='Output directory')
    args = parser.parse_args()
    return args


def main():
    args = manage_cmd()
    errors = {}
    if args.out_dir and os.path.isdir(args.out_dir):
        out_dir = args.out_dir
    else:
        out_dir = os.getcwd()
    book = Book_fb2()
    templates = Common.get_templates()
    if args.template not in templates:
        errors['template'] = 'No such template: ' + args.template
    else:
        name_format = templates[args.template]
        if args.format:
            name_format = args.format
        input_files = get_files_to_work_with(args.fname, ['fb2'], a_recursive=args.recursive)
        for fname in input_files:
            try:
                book.open(fname)
                name = format_name(book, name_format)
                if not name:
                    raise Exception('Result filename is empty')
                name = unicode(Common.validate_filename(name + '.fb2'))
            except:
                errors[fname] = sys.exc_info()[1]
                continue
            name = name.strip('\n ')
            print fname, ' => ', name
            if not args.dryrun:
                try:
                    name = os.path.join(out_dir, name)
                    Common.ensure_path_exists(os.path.dirname(name))
                    os.rename(fname, name)
                except:
                    errors[fname] = sys.exc_info()[1]

    print 'Errors: '
    for e in errors:
        print '  ' + e + ':', errors[e]


if __name__ == '__main__':
    main()
