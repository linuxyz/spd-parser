#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Tuple, Iterator
import math

__all__ = ["column_to_index",
           "index_to_column",
           "name_to_axis",
           "name_to_pos",
           "range_to_cells",
           "XCell",
           "XRange"]


def column_to_index(col: str) -> int:
    """Convert from Excel Column Name to Number format.

    e.g. 'A'->1, 'Z'->26, 'AA'->27, 'XFD'->16384

    Parameters:
      col (str): Excel Column name, e.g. 'A1', 'XFD1'

    Returns:
      int: Number base Column ID
    """
    rtn, m = 0, 1
    coll = [c for c in col.upper() if ord('A') <= ord(c) <= ord('Z')]
    for c in reversed(coll):
        # calculate the value
        rtn += (ord(c) - ord('A') + 1) * m
        m *= 26  # = ord('Z')-ord('A')
    return rtn


def index_to_column(num: int) -> str:
    """Convert Number ID to Excel Column name.

    Parameters:
      num (int): Excel Column ID in number format

    Returns:
      str: Excel Column Name, e.g. '$A$1'
    """
    if num <= 1 or num > 16384:
        return 'A'
    col = ''
    num, v = divmod(num, 26)
    while num > 0 or v > 0:
        if v == 0:
            num -= 1
            v = 26
        col = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[v - 1] + col
        num, v = divmod(num, 26)
    return col


def name_to_axis(cell: str) -> Tuple[str, int]:
    """From Cell name to Axis position.

    e.g. 'A10' to ('A', 10)

    Parameters:
      cell (str): Cell name str

    Returns:
      Tuple[str, int]: a Tuple of [Colume name, row ID]
    """
    idx, row = 0, 0
    for n in cell:
        if n.isnumeric():
            break
        idx += 1
    if idx < len(cell):
        row = int(cell[idx:])
    return cell[:idx], row


def name_to_pos(cell: str) -> Tuple[int, int]:
    """From Cell name to index.

    e.g. 'A10' to (1, 10)

    Parameters:
      cell (str): Cell name str

    Returns:
      Tuple[int, int]: a Tuple coresponding the position of cell.
    """
    i = 0
    for n in cell:
        if n.isnumeric():
            break
        i += 1
    if i < len(cell):
        i = int(cell[i:])
    else:
        i = 0
    return column_to_index(cell), i


# Internal ranges
_MOST_USED_COLUMNS = [
    '',
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
    'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
    'AA', 'AB', 'AC', 'AD', 'AE', 'AF', 'AG', 'AH', 'AI', 'AJ', 'AK', 'AL', 'AM',
    'AN', 'AO', 'AP', 'AQ', 'AR', 'AS', 'AT', 'AU', 'AV', 'AW', 'AX', 'AY', 'AZ',
    'BA', 'BB', 'BC', 'BD', 'BE', 'BF', 'BG', 'BH', 'BI', 'BJ', 'BK', 'BL', 'BM',
    'BN', 'BO', 'BP', 'BQ', 'BR', 'BS', 'BT', 'BU', 'BV', 'BW', 'BX', 'BY', 'BZ',
    'CA', 'CB', 'CC', 'CD', 'CE', 'CF', 'CG', 'CH', 'CI', 'CJ', 'CK', 'CL', 'CM',
    'CN', 'CO', 'CP', 'CQ', 'CR', 'CS', 'CT', 'CU', 'CV', 'CW', 'CX', 'CY', 'CZ'
]


def range_to_cells(cellrange: str) -> Iterator:
    """Return all cells within a RANGE:RANGE.
    e.g. A1:C10 -> [A1,A2,A3,..,A10,B1,..,B10,C1,..,C10]
    """
    ab = cellrange.split(':')
    if len(ab) <= 1:
        yield cellrange
        return

    # for Range, we loop the row first, then column
    left, top = name_to_pos(ab[0])
    right, bottom = name_to_pos(ab[1])

    for c in range(left, right+1):
        if c < len(_MOST_USED_COLUMNS):
            colume = _MOST_USED_COLUMNS[c]
        else:
            colume = index_to_column(c)

        for r in range(top, bottom+1):
            yield "{:s}{:d}".format(colume, r)


class XCell:
    """A cell identified by (x,y) coordinates.

    supports: +, -, *, /, str, repr

    length  -- calculate length of vector to point from origin
    distance_to  -- calculate distance between two points
    as_tuple  -- construct tuple (x,y)
    clone  -- construct a duplicate
    """

    def __init__(self, x: int = 0, y: int = 0) -> None:
        """Init with x, y."""
        self.x: int = x
        self.y: int = y

    def __add__(self, p):
        """XCell(x1+x2, y1+y2)."""
        return XCell(self.x + p.x, self.y + p.y)

    def __sub__(self, p):
        """XCell(x1-x2, y1-y2)."""
        return XCell(self.x - p.x, self.y - p.y)

    def __mul__(self, scalar):
        """XCell(x1*x2, y1*y2)."""
        return XCell(self.x * scalar, self.y * scalar)

    def __div__(self, scalar):
        """XCell(x1/x2, y1/y2)."""
        return XCell(self.x / scalar, self.y / scalar)

    def __str__(self):
        """Represent XCell as str."""
        return "(%d, %d)" % (self.x, self.y)

    def __repr__(self):
        """Represent XCell as str."""
        return "%s(%r, %r)" % (self.__class__.__name__, self.x, self.y)

    def length(self):
        """Length of the XCell to (0, 0)."""
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def distance_to(self, p):
        """Calculate the distance between two points."""
        return (self - p).length()

    def as_tuple(self):
        """Return (x, y):Tuple."""
        return self.x, self.y

    def clone(self):
        """Return a full copy of this point."""
        return XCell(self.x, self.y)

    @staticmethod
    def new(cell: str):
        """Create XCell from str."""
        x, y = 0, 0
        if len(cell) > 0:
            x = column_to_index(cell)
            y = int(
                ''.join([r for r in cell if ord('0') <= ord(r) <= ord('9')]))
        return XCell(x, y)


class XRange:
    """A range identified by two points both points are included.

    The rectangle stores left, top, right, and bottom values.

    Coordinates are based on screen coordinates.

    origin                               top
       +-----> x increases                |
       |                           left  -+-  right
       v                                  |
    y increases                         bottom

    botom-right: XFD1048576

    set_points  -- reset rectangle coordinates
    contains  -- is a Cell inside?
    overlaps  -- does a rectangle overlap?
    top_left  -- get top-left corner
    bottom_right  -- get bottom-right corner
    """

    def __init__(self, rg: str) -> None:
        """Initialize a excel range from string."""
        (head, _, tail) = rg.partition(':')
        x1, y1 = XCell.new(head).as_tuple()
        (x2, y2) = (x1, y1)
        if len(tail):
            x2, y2 = XCell.new(tail).as_tuple()
        self.left = min(x1, x2)
        self.top = min(y1, y2)
        self.right = max(x1, x2)
        self.bottom = max(y1, y2)

    def as_tuple(self):
        """((x, y),(x2,y2))"""
        return (self.left, self.top), (self.right, self.bottom)

    def contains(self, pt: XCell) -> bool:
        """Return true if a point is inside the rectangle."""
        x, y = pt.as_tuple()
        return (self.left <= x <= self.right and
                self.top <= y <= self.bottom)

    def overlaps(self, other) -> bool:
        """Return true if a rectangle overlaps this rectangle."""
        return (self.right > other.left and self.left < other.right and
                self.top < other.bottom and self.bottom > other.top)

    def top_left(self) -> XCell:
        """Return the top-left corner as a XCell."""
        return XCell(self.left, self.top)

    def bottom_right(self) -> XCell:
        """Return the bottom-right corner as a XCell."""
        return XCell(self.right, self.bottom)

    def length(self) -> int:
        """Return the total number of cells in this Range."""
        return (self.right - self.left + 1) * (self.bottom - self.top + 1)

    @property
    def __str__(self) -> str:
        """Represent XRange as String."""
        return "<XRange (%s,%s)-(%s,%s)>" % (self.left, self.top, self.right, self.bottom)

    def __repr__(self) -> str:
        """Represent XRange as String."""
        return "%s(%r, %r)" % (self.__class__.__name__,
                               XCell(self.left, self.top),
                               XCell(self.right, self.bottom))

# vim: noai:ts=4:sw=4:expandtab
