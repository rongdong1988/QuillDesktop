#!/usr/bin/env python
# vim: set fileencoding=utf-8
# Copyright (C) 2012, Nicholas Knouf
#
# This file is part of quill_utils
#
# quill_utils is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import StringIO
import os
import shutil
import struct
import sys
import tarfile
import tempfile
import uuid

from optparse import OptionParser

import cairo

__version__ = 0.01

class QuillPage(object):
    def __init__(self, page_path = None, page_number = 1, output_dir = None):
        self.page_path = page_path
        self.page_number = page_number
        self.output_dir = output_dir

        with open(page_path, "rb") as fp:

            self.version = struct.unpack(">i", fp.read(4))
            nbytes = struct.unpack(">h", fp.read(2))
            self.u = fp.read(36)
            self.tsversion = struct.unpack(">i", fp.read(4))
            
            self.ntags = struct.unpack(">i", fp.read(4))
            foo = struct.unpack(">i", fp.read(4))
            foo = struct.unpack(">i", fp.read(4))
            
            self.paper_type = struct.unpack(">i", fp.read(4))
            self.nimages = struct.unpack(">i", fp.read(4))
            dummy = struct.unpack(">i", fp.read(4))
            self.read_only = struct.unpack(">?", fp.read(1))
            self.aspect_ratio = struct.unpack(">f", fp.read(4))
            self.nstrokes = struct.unpack(">i", fp.read(4))
            
            self.width = 850
            self.height = 1100

            if self.output_dir is not None:
                try:
                    os.mkdir(self.output_dir)
                except OSError:
                    pass

                surface = cairo.SVGSurface(os.path.join(self.output_dir, "page_%03d.svg" % self.page_number), self.width, self.height)
            else:
                surface = cairo.SVGSurface("page_%03d.svg" % self.page_number, self.width, self.height)
            cr = cairo.Context(surface)
            cr.set_source_rgb(0, 0, 0)
            cr.set_line_cap(cairo.LINE_CAP_ROUND)
            cr.set_line_join(cairo.LINE_JOIN_ROUND)
            cr.set_line_width(0.003)
            cr.translate(.010, .010)
            cr.scale(self.width, self.height)
            
            
            for stroke in xrange(self.nstrokes[0]):
                sversion = struct.unpack(">i", fp.read(4))
                pen_color = struct.unpack(">i", fp.read(4))
                pen_thickness = struct.unpack(">i", fp.read(4))
                toolint = struct.unpack(">i", fp.read(4))
                N = struct.unpack(">i", fp.read(4))
            
                points = []
                for instance in xrange(N[0]):
                    x = struct.unpack(">f", fp.read(4))
                    y = struct.unpack(">f", fp.read(4))
                    p = struct.unpack(">f", fp.read(4))
                    points.append((x[0], y[0], p[0]))
                
                for point in xrange(len(points) - 1):
                    cr.set_line_width(0.003 * ((points[point][2] + points[point+1][2])/2))
                    cr.move_to(points[point][0], points[point][1])
                    cr.line_to(points[point + 1][0], points[point + 1][1])
                    cr.stroke()
                cr.close_path()
            
                cr.save()
            
            self.nlines = struct.unpack(">i", fp.read(4))
            dummy = struct.unpack(">i", fp.read(4))
            self.ntext = struct.unpack(">i", fp.read(4))

class QuillIndex(object):
    def __init__(self, index_path = None):
        self.index_path = index_path

        with open(index_path, "rb") as fp:
            self.version = struct.unpack(">i", fp.read(4))
            self.npages = struct.unpack(">i", fp.read(4))
            
            self.pages = []
            
            for x in xrange(self.npages[0]):
                nbytes = struct.unpack(">h", fp.read(2))
                u = fp.read(36)
                self.pages.append(u)
            
            self.currentPage = struct.unpack(">i", fp.read(4))
            
            nbytes = struct.unpack(">h", fp.read(2))
            self.title = fp.read(nbytes[0])
            
            self.ctime = struct.unpack(">q", fp.read(8))
            self.mtime = struct.unpack(">q", fp.read(8))
            nbytes = struct.unpack(">h", fp.read(2))
            self.u = fp.read(36)

if __name__ == "__main__":

    parser = OptionParser()
    parser.add_option("-f", "--filename", dest="filename", help = "Quill filename to convert into SVG")

    (options, arges) = parser.parse_args()

    if (options.filename is None):
        print "Filename is required"
        sys.exit(-1)

    u, ext = os.path.splitext(options.filename)
    with tarfile.open(options.filename, "r") as t:
        tempdir = tempfile.mkdtemp()
        t.extractall(path=tempdir)
        index_path = os.path.join(tempdir, "notebook_%s" % u, "index.quill_data")
        q = QuillIndex(index_path = index_path)
        
        page_number = 1
        for page in q.pages:
            qp = QuillPage(page_path = os.path.join(tempdir, "notebook_%s" % u, "page_%s.quill_data" % page), page_number = page_number, output_dir = q.title)
            page_number += 1
        shutil.rmtree(tempdir)
