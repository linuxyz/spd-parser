#!/usr/bin/env python3

import sys
import openpyxl as xl

if len(sys.argv) == 1:
    print(f"Usage: {sys.argv[0]} <excel-file.xlsx>")
    exit(-1)

FN = sys.argv[1]

wb = xl.load_workbook(filename=FN)

for n in wb.defined_names.localnames(None):
    print(f"{n} := {wb.defined_names[n].attr_text}")

for s in wb:
    for col in s.columns:
        for c in col:
            if c.value:
                # print(dir(c))
                sp = "@" if len(c.value) > 1 and c.value[0] == '=' else "@="
                print(f"'{c.parent.title}'!{c.coordinate} {sp}{c.value}")
