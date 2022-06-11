#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List, ClassVar
# import pprint as pp


# this is one formula
class XFormula:
    """ Cell of a sheet """
    CT_UNKNOWN: ClassVar[int] = 0
    CT_STATIC: ClassVar[int] = 1
    CT_ACTIVE: ClassVar[int] = 2
    CT_TARGET: ClassVar[int] = 4

    def __init__(self,
                 sheet: str, syntax: List, params: List, values: List,
                 ln: int = -1, txt: str = None) -> None:
        """"Default init."""
        # line number in the text file
        self.ln: int = ln
        self.txt: str = txt
        # str: target sheet name
        self.sheet: str = sheet
        self.syntax: List = syntax
        self.params: List = params
        self.values: List = values

        # output cells will be drived by this cell
        self.outputs: List = []

        # extended attributes, need to analytics by parsing the syntax
        self.targets: List = []

        # type of cell - It will be evaluated by EEIEngine.evaluate_types(formula)
        #   0: unspecified,
        #   1: static value
        #   2: active (value can be changed time to time)
        #   4: target cell
        self.type: int = XFormula.CT_UNKNOWN

    def settypes(self, act: bool, tgt: bool) -> int:
        """Set the formula type: act - active cell; tgt - output cell."""
        if act:
            self.type |= XFormula.CT_ACTIVE
        if tgt:
            self.type |= XFormula.CT_TARGET
        return self.type

    def ingress(self):
        """Return XFormula itself if it contains source/input/active functinos."""
        return self if self.type & XFormula.CT_ACTIVE > 0 else None

    def egress(self) -> bool:
        """Return XFormula itself if it contains output functinos."""
        return self if self.type & XFormula.CT_TARGET > 0 else None

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"""FORMULA:{self.ln:06d},  TXT:`{self.txt}`, TYPE:{self.type:04b},
               SHEET:'{self.sheet}',  TARGET:{self.targets},
               PARAMS:{self.params},
               VALUES:{self.values},
               SYNTAX:{self.syntax}"""


def new(sheet: str,
        syntax: List, params: List, values: List,
        ln: int, txt: str = None) -> XFormula:
    """Function to create a new XFormula object."""
    return XFormula(sheet, syntax, params, values, ln, txt)


#############################################################################
if __name__ == '__main__':
    print(__name__)

# vim: noai:ts=4:sw=4:expandtab
