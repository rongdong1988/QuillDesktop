"""
Export to Portable Document Format (PDF)

EXAMPLES::

    >>> from quill.exporter.pdf import Pdf
    >>> from tempfile import TemporaryFile
    >>> tmp = TemporaryFile(suffix='pdf')
    >>> Pdf(tmp).book(sample_book)
    >>> Pdf(tmp).book(sample_book_xoj)
"""

import cairo

from quill.exporter.cairo_surface_paginated import CairoSurfacePaginated


class Pdf(CairoSurfacePaginated):
    """
    Exporter to PDF
    
    :param fileobj: a filename or a file-like object
    """
    
    def __init__(self, fileobj):
        """
        The Python constructor
        """
        surface = cairo.PDFSurface(fileobj, 1, 1)
        super(Pdf, self).__init__(surface)

