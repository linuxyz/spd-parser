################################################################################
# Unit Tests
import unittest

from spd.Utils import range_to_cells, column_to_index, index_to_column, name_to_pos, XCell, XRange


class TestRangeToCells(unittest.TestCase):
    def test_rangetocells(self):
        self.assertEqual(['A1'], list(range_to_cells("A1")))
        self.assertEqual(['A2', 'B2', 'C2'], list(range_to_cells("A2:C2")))
        self.assertEqual(['A2', 'B2', 'C2'], list(range_to_cells("A2:C2")))
        self.assertEqual(['A1', 'A2', 'B1', 'B2', 'C1', 'C2'],
                         list(range_to_cells("A1:C2")))
        self.assertEqual(['XFD8', 'XFD9', 'XFD10'],
                         list(range_to_cells('XFD8:XFD10')))


class TestEEIColumnMethods(unittest.TestCase):
    """
    Test cases: 'A'->1, 'Z'->26, 'AA'->27, 'XFD'->16384
    """
    test_data = (('A', 1, 0),
                 ('A100', 1, 100),
                 ('Z', 26, 0),
                 ('AA', 27, 0),
                 ('AA900', 27, 900),
                 ('AZ', 52, 0),
                 ('IV', 256, 0),
                 ('ZZ', 702, 0),
                 ('ZZ1', 702, 1),
                 ('AAA', 703, 0),
                 ('AZZ', 1378, 0),
                 ('XFD', 16384, 0))

    def test_colToNum(self):
        for tp in self.test_data:
            self.assertEqual(column_to_index(tp[0]), tp[1])

    def test_numToCol(self):
        for tp in self.test_data:
            self.assertTrue(tp[0].startswith(index_to_column(tp[1])))

    def test_nameToPos(self):
        for tp in self.test_data:
            self.assertEqual(name_to_pos(tp[0]), (tp[1], tp[2]))


class TestEEIUtils(unittest.TestCase):
    """
    Test cases: 'A'->1, 'Z'->26, 'AA'->27, 'XFD'->16384
    """
    test_data = (('A1', (1, 1)),
                 ('Z2', (26, 2)),
                 ('AA3', (27, 3)),
                 ('AZ4', (52, 4)),
                 ('IV65536', (256, 65536)),
                 ('ZZ5', (702, 5)),
                 ('AAA6', (703, 6)),
                 ('AZZ7', (1378, 7)),
                 ('XFD8', (16384, 8)),
                 ('XFD65536', (16384, 65536)))

    test_data2 = (('A1:B2', ((1, 1), (2, 2)), 'A2', True),
                  ('Z2:AA3', ((26, 2), (27, 3)), 'AA2', True),
                  ('AA3:AB4', ((27, 3), (28, 4)), 'AB3', True),
                  ('AZ4:AZ6', ((52, 4), (52, 6)), 'AZ5', True),
                  ('IV65536:ZZ100000', ((256, 65536), (702, 100000)), 'ZZ65537', True),
                  ('ZZ5:ZZ10', ((702, 5), (702, 10)), 'ZZ4', False),
                  ('AAA6:AAA10', ((703, 6), (703, 10)), 'AAA11', False),
                  ('AZZ7:AZZ77', ((1378, 7), (1378, 77)), 'AZZ78', False),
                  ('XFD8:XFD80', ((16384, 8), (16384, 80)), 'XFD80', True),
                  ('XFD65536:XFD100000', ((16384, 65536), (16384, 100000)), 'XFD65537', True))

    def test_cell(self):
        for tp in self.test_data:
            self.assertEqual(XCell.new(tp[0]).as_tuple(), tp[1])

    def test_range1(self) -> None:
        for tp in self.test_data:
            self.assertEqual(XRange(tp[0]).as_tuple()[0], tp[1])
            a, b = XRange(tp[0]).as_tuple()
            self.assertEqual(a, b)

    def test_range2(self) -> None:
        for tp in self.test_data2:
            self.assertEqual(XRange(tp[0]).as_tuple(), tp[1])
            self.assertEqual(XRange(tp[0]).contains(
                XCell.new(tp[2])), tp[3])


#############################################################################
# Unit Test
if __name__ == '__main__':
    unittest.main()
