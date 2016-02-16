# -*- coding: utf-8 -*-
#########################################################################
#
# StreamingXMLWriter
#
# Copyright (c) 2015-2016 ACSONE SA/NV, All rights reserved.
# Author: Stéphane Bidoul <stephane.bidoul@acsone.eu>
#
# This python module is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3.0 of the License, or (at your option) any later version.
#
# This python library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this python module.
#
#########################################################################

from collections import OrderedDict
from contextlib import contextmanager
from xml.sax.saxutils import XMLGenerator
from xml.sax.xmlreader import AttributesNSImpl

import six


__all__ = ['StreamingXMLWriter']


class MyXMLGenerator(XMLGenerator):
    """ XMLGenerator subclass that supports comments """

    def comment(self, comment):
        # inspired by XMLGenerator.characters()
        if comment:
            try:
                self._finish_pending_start_element()
            except AttributeError:
                # not in all XMLGenerator implementations
                pass
            if isinstance(comment, six.binary_type):
                comment = comment.decode(self._encoding)
            self._write(u'<!--')
            self._write(comment)
            self._write(u'-->')


class StreamingXMLWriter(object):
    """ Streaming XML Writer

    A pythonic, lightweight class to write XML in a pythonic
    and standard compliant way.

    >>> from io import BytesIO
    >>> from __future__ import print_function
    >>> from collections import OrderedDict

    >>> def bprint(s):
    ...     if not isinstance(s, str):
    ...         s = s.decode()
    ...     print(s)

    Example without namespace:

    >>> s = BytesIO()
    >>> with StreamingXMLWriter(s) as writer:
    ...    with writer.element("root"):
    ...        with writer.element("e", {'a': '1'}):
    ...            writer.characters("content")
    ...        with writer.element("e"):
    ...            pass
    ...        writer.processing_instruction("target", "data")
    >>> bprint(s.getvalue())
    <?xml version="1.0" encoding="utf-8"?>
    <root><e a="1">content</e><e></e><?target data?></root>

    Example with namespaces:

    >>> s = BytesIO()
    >>> with StreamingXMLWriter(s) as writer:
    ...    writer.start_namespace("myns", "http://mynamespace.org/")
    ...    with writer.element("myns:root"):
    ...        writer.characters("\\n")
    ...        with writer.element("myns:e", {'a': '1'}):
    ...            writer.characters("content")
    ...        with writer.element("myns:e"):
    ...            pass
    >>> bprint(s.getvalue())
    <?xml version="1.0" encoding="utf-8"?>
    <myns:root xmlns:myns="http://mynamespace.org/">
    <myns:e a="1">content</myns:e><myns:e></myns:e></myns:root>

    Example with default namespace (prefix=None):

    >>> s = BytesIO()
    >>> with StreamingXMLWriter(s) as writer:
    ...     writer.start_namespace(None, "http://mynamespace.org/")
    ...     with writer.element("root"):
    ...         with writer.element("e", {"a": "1"}):
    ...             pass
    >>> bprint(s.getvalue())
    <?xml version="1.0" encoding="utf-8"?>
    <root xmlns="http://mynamespace.org/"><e a="1"></e></root>

    Example with explicit closing (more verbose but could be useful too):

    >>> s = BytesIO()
    >>> writer = StreamingXMLWriter(s)
    >>> writer.start_element("root")
    >>> writer.start_element("e", OrderedDict([('a', '1'), ('b', '2')]))
    >>> writer.characters("content")
    >>> writer.end_element("e")
    >>> writer.start_element("e")
    >>> writer.end_element("e")
    >>> writer.end_element("root")
    >>> bprint(s.getvalue())
    <?xml version="1.0" encoding="utf-8"?>
    <root><e a="1" b="2">content</e><e></e></root>

    Text element:

    >>> s = BytesIO()
    >>> writer = StreamingXMLWriter(s)
    >>> writer.text_element('root', {'a': '1'}, 'contenté')
    >>> bprint(s.getvalue())
    <?xml version="1.0" encoding="utf-8"?>
    <root a="1">contenté</root>

    Comment:
    >>> s = BytesIO()
    >>> writer = StreamingXMLWriter(s)
    >>> with writer.element("root"):
    ...     writer.comment("commenté")
    >>> bprint(s.getvalue())
    <?xml version="1.0" encoding="utf-8"?>
    <root><!--commenté--></root>
    """

    def __init__(self, f, encoding='utf-8'):
        self._ns = {}  # prefix: uri
        self._g = MyXMLGenerator(f, encoding)
        self._g.startDocument()

    def close(self):
        self._g.endDocument()

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.close()

    def start_namespace(self, prefix, uri):
        """ Declare a namespace prefix

        Use prefix=None to set the default namespace.
        """
        self._g.startPrefixMapping(prefix, uri)
        self._ns[prefix] = uri

    def end_namespace(self, prefix):
        """ Undeclare a namespace prefix. """
        del self._ns[prefix]
        self._g.endPrefixMapping(prefix)

    def resolve_namespace(self, qname):
        """ Obtain (uri, name) from a qualified name """
        if ':' in qname:
            prefix, name = qname.split(':', 1)
            uri = self._ns[prefix]
        else:
            name = qname
            if None in self._ns:
                uri = self._ns[None]
            else:
                uri = None
        return (uri, name)

    def start_element(self, qname, attrs={}):
        name = self.resolve_namespace(qname)
        attr_vals = OrderedDict()
        attr_qnames = OrderedDict()
        for attr_qname, attr_val in attrs.items():
            attr_name = self.resolve_namespace(attr_qname)
            attr_vals[attr_name] = attr_val
            attr_qnames[attr_name] = attr_qname
        attrs_ns = AttributesNSImpl(attr_vals, attr_qnames)
        self._g.startElementNS(name, qname, attrs_ns)

    def end_element(self, qname):
        name = self.resolve_namespace(qname)
        self._g.endElementNS(name, qname)

    @contextmanager
    def element(self, qname, attrs={}):
        self.start_element(qname, attrs)
        yield self
        self.end_element(qname)

    def characters(self, content):
        self._g.characters(content)

    def text_element(self, qname, attrs={}, content=None):
        with self.element(qname, attrs):
            if content:
                self.characters(content)

    def processing_instruction(self, target, data):
        self._g.processingInstruction(target, data)

    def comment(self, comment):
        self._g.comment(comment)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
