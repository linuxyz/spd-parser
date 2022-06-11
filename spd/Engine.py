#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List  # Dict, Tuple, Union, ClassVar

from Formula import XFormula
# import EEISyntax
# import EEIUtils


""" Engine level configuration
it defines all the supported functions!
- Active Functions which could trigger the calculation
- Output Functions which generate outputs

=TR(universe, fields, parameters, cell)
"""

xlsFuncs: List[str] = []
xlsActiveFuncs: List[str] = ['RTGET', 'TR', 'TODAY', 'NOW']
xlsEgressFuncs: List[str] = ['RTC', 'OUTPUT']


def load(yaml: str):
    """Load all the pre-defined things for Engine."""
    pass


def _expand_deps(expr: XFormula, line: str):
    """Excel function may overwrite/output to other cells.
    e.g. `=TR(RIC,FIELDS,target)`, the target cells will be overwrite by this cell
    so it gives the XFormula and original text to make it extend the target outputs
    """
    pass


def _cell_types(expr: XFormula) -> bool:
    """Whether the cell is: ingress and/or egress."""
    act, out = False, False
    for f in expr.syntax:
        if not act:
            if f[1] in xlsActiveFuncs:
                act = True
        if not out:
            if f[1] in xlsEgressFuncs:
                out = True
        if act and out:
            break
    expr.settypes(act, out)
    return out


def evaluate_funcs(expr: XFormula, line: str):
    _expand_deps(expr, line)
    _cell_types(expr)

# vim: noai:ts=4:sw=4:expandtab
