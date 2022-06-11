#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# import pprint as pp
from typing import Dict, List, Tuple

from . import Utils
from .Formula import XFormula

"""
Each egress cell can construct a call graph -- DAG.
The DAGs shoud be merged if there is/are shared ingress cell(s) across DAGs;

So generally there are several conditions:
#. [egress] -> ...                                            -- this is a static output
#. [egress] -> ... -> [ingress] -> ... ->                     -- this is dynamic output
#. [egress] -> ... -> [ingress] -> ... -> [ingress] -> ...    -- this is a loop condition
Here it can't discover the senarios which ingress only tree because those ingress cell will be by-passed
"""


class XProgram:
    """ Represent as one XLSX file.
    Record Single cell Formulas, Range Formulas, Refer cells, Static values as:
    `self.sheetsExpr`, `self.sheetsRange`, `self.sheetsRefer`, `self.sheetsValue` .
    All the ingress and egress cells are also recorded to reflect the callflows.
    """

    def __init__(self):
        # Store all the XFormula as Dict[str, Dict[str, XFormula]]
        self.sheetsExpr: Dict[str, Dict[str, XFormula]] = {}
        # Store all the range of sheets as Dict[sheet:str, List[Tuple[topleft, bottomright, XFormula]]]
        self.sheetsRange: Dict[str, List[Tuple]] = {}
        # Store all the Ref and Alias as Dict[sheet:str, Dict[str, Tuple[sheet:str, cellrange:str]]]
        self.sheetsRefer: Dict[str, Dict[str, Tuple[str, str]]] = {"": {}}
        # Store all the static value as Dict[sheet:str, Dict[cell:str, value:str]]
        self.sheetsValue: Dict[str, Dict[str, str]] = {
            '': {'FALSE': False, 'TRUE': True}}

        # All active cells: List[XFormula]
        self.ingressCells: List[XFormula] = []

        # Original output/egress Cells - List[XFormula]
        self.egressCells: List[XFormula] = []

        # call flow from cell to cell for all Egress Functions
        self.callflow = []

        # call flows for Active cells to other Active cells
        # it is ActiveCell => array of ref(XFormula)
        self.dataPrepares = {}  # { ActiveCell: [array of XFormula], ... }
        pass

    def add_refer(self, href: Tuple[str, str], tgt: str, sheet: str = ''):
        """ Add alias and refer into the program
        XXX: We assume the ALIAS always come at the beginning.
        """
        if sheet not in self.sheetsRefer:
            self.sheetsRefer[sheet] = {tgt: href}
        else:
            self.sheetsRefer[sheet][tgt] = href
        pass

    def add_formula(self, cell: XFormula, tgt: str, sheet: str = ''):
        """ Before set the cell into the sheets, please make sure call `EEIEngine.evaluate_funcs(cell)` to
        expand the extra outpus and validate the type of the cell!!!
        """
        if sheet not in self.sheetsExpr:
            self.sheetsExpr[sheet] = {tgt: cell}
        else:
            self.sheetsExpr[sheet][tgt] = cell
        # Record all the target Cells
        if cell.egress():
            self.egressCells.append(cell)
        # Record all active cells
        if cell.ingress():
            self.ingressCells.append(cell)

        # For range, let's put then into a special list
        rg = tgt.split(':')
        if len(rg) > 1:
            topleft, bottomright = Utils.name_to_pos(
                rg[0]), Utils.name_to_pos(rg[1])
            if sheet in self.sheetsRange:
                self.sheetsRange[sheet].append((topleft, bottomright, cell))
            else:
                self.sheetsRange[sheet] = [(topleft, bottomright, cell)]

    def add_value(self, value: str, tgt: str, sheet: str = ''):
        """ Add static value to this program!
        """
        if sheet not in self.sheetsValue:
            self.sheetsValue[sheet] = {tgt: value}
        else:
            self.sheetsValue[sheet][tgt] = value
        pass

    def _overlapped_range(self, sheet: str, cellrange: str) -> XFormula:
        """ Whether the input range/cell is overlapped with range, and it doesn't visited by `tgt`
        """
        if sheet not in self.sheetsRange:
            return None
        rg = cellrange.split(':')
        if len(rg) == 1:      # only one cell
            x, y = Utils.name_to_pos(rg[0])
            for r in self.sheetsRange[sheet]:
                if r[0][0] <= x <= r[1][0] and r[0][1] <= y <= r[1][1]:
                    return r[2]
        else:                 # ranges over-cross
            x1, y1 = Utils.name_to_pos(rg[0])
            x2, y2 = Utils.name_to_pos(rg[1])
            for r in self.sheetsRange[sheet]:
                if x1 <= r[1][0] and r[0][0] <= x2 and y1 <= r[1][1] and r[0][1] <= y2:
                    return r[2]
        return None

    def _ref_first_search(self, ref: Tuple[str, str], tgt: int, visited: List):
        """ Search and append all the `ref:Tuple[sheet:str, cellrange:str]` into the `visited`
        """
        sheet, cellrange = ref
        if cellrange.rfind(':') < 0:
            self._ref_first_search_cell(ref, tgt, visited)
            return

        # print("  TGT:{:06d} -> '{}'!{}".format(tgt, sheet, cellrange))
        # Look for all the cells again
        r = self._overlapped_range(sheet, cellrange)
        if r and tgt not in r.outputs:
            #print("  -> TGT:{:06d} -> R:'{}'!{}".format(tgt, sheet, cellrange))
            r.outputs.append(tgt)
            visited.append(r)

        # loop all cells, but do deep-first for all ref cells
        sheetcells = self.sheetsExpr[sheet] if sheet in self.sheetsExpr else {}
        sheetrefs = self.sheetsRefer[sheet] if sheet in self.sheetsRefer else {
        }
        for x in Utils.range_to_cells(cellrange):
            #print("  -> TGT:{:06d} -> C:'{}'!{}".format(tgt, sheet, x))
            if x in sheetcells:
                # but here it could be: Value, Ref, Alias
                fn = sheetcells[x]
                if tgt not in fn.outputs:
                    fn.outputs.append(tgt)
                    visited.append(fn)
            elif x in sheetrefs:
                self._ref_first_search(sheetrefs[x], tgt, visited)

    def _ref_first_search_cell(self, ref: Tuple[str, str], tgt: int, visited: List):
        """ Search and append all the cell into the `visited`
        """
        sheet, cell = ref
        #print("  TGT:{:06d} -> '{}'!{}".format(tgt, sheet, cell))
        # Look for all the cells again
        r = self._overlapped_range(sheet, cell)
        if r:
            if tgt not in r.outputs:
                #print("  -> TGT:{:06d} -> R:'{}'!{}".format(tgt, sheet, cell))
                r.outputs.append(tgt)
                visited.append(r)
            return

        # loop all cells, but do deep-first for all ref cells
        sheetcells = self.sheetsExpr[sheet] if sheet in self.sheetsExpr else {}
        if cell in sheetcells:
            #print("  -> TGT:{:06d} -> E:'{}'!{}".format(tgt, sheet, cell))
            fn = sheetcells[cell]
            if tgt not in fn.outputs:
                fn.outputs.append(tgt)
                visited.append(fn)
            return

        # loop all Ref and Alias
        sheetrefs = self.sheetsRefer[sheet] if sheet in self.sheetsRefer else {
        }
        if cell in sheetrefs:   # It must be a Tuple[sheet:str, cellrange:str]
            #print("  -> TGT:{:06d} -> A:'{}'!{}".format(tgt, sheet, cell))
            self._ref_first_search(sheetrefs[cell], tgt, visited)
            return

    def breathfistsearch(self, tgt: XFormula, visited: List[XFormula] = []):
        """ Breath-First Search to go through all the cells which depeneded by tgt: target cell
        """
        if not visited or len(visited) == 0:
            visited, idx = [tgt], 0
        else:
            idx = len(visited)
            visited.append(tgt)

        while idx < len(visited):
            it = visited[idx]
            params = []
            for c in it.params:   # c is a ref,range,alias
                # pp.pprint(tgt.ln, c)
                if isinstance(c, Tuple):    # Alias or Ref
                    if len(c[0]) == 0:        # Alias
                        sheet, cellrange = self.sheetsRefer[""][c[1]]
                    else:                     # Ref
                        sheet, cellrange = c
                else:                       # in sheet ref
                    sheet, cellrange = it.sheet, c
                # Added to a new list if it doesn't exist
                ref = (sheet, cellrange)
                # No duplications
                if ref not in params:
                    params.append(ref)

            # Debug - .txt is only available in debug mode
            if it.txt:
                print("ID:{:04d} TGT:{:06d}: TXT:{}".format(
                    idx, tgt.ln, it.txt))
            # else:
            #  print("ID:{:04d} TGT:{:06d}: S:{} P:{} V:{}".format(idx, tgt.ln, it.syntax, it.params, it.values))

            # Loop all params
            for c in params:
                self._ref_first_search(c, tgt.ln, visited)

            # next one
            idx += 1

        return visited

    def build_call_trees(self):
        """ Build call trees by
        1, loop all the egressCells, build the dependencies cells from egress to all depended cells
        2, mark all the activate cells during the trace, merge the callflow for egressCells
        3, reverse the dependency trees to callflow
        """
        dags: Dict = {}
        for tgt in self.egressCells:
            dags[tgt.ln] = self.breathfistsearch(tgt)

        # Now all the ingressCells should record all the egress ln.
        # We do only group by

        pass


# vim: noai:ts=4:sw=4:expandtab
