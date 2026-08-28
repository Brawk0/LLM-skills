"""Synthetic regression cases for object IDs and electrical endpoints."""

import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import inspect_diptrace_ascii as inspector


def part(number, *, ref="U1", ordinal=0, pin="1", net=4):
    identifier = f"      (Number {number})\n" if number is not None else ""
    return f'''    (Part "generic" "{ref}"
{identifier}      (PartName "Unit {pin}")
      (Pins
        (Pin {ordinal}
          (Number 1)
          (StringNumber "{pin}")
          (Name "IO")
          (NetNumber {net})
        )
      )
    )'''


def net(number, pairs, *, geometry=False):
    members = "\n".join(f"        (pt {obj} {pin})" for obj, pin in pairs)
    drawing = "      (Lines\n        (pt 999 0)\n      )\n" if geometry else ""
    return f'''    (Net "SIGNAL_{number}"
      (Number {number})
      (Parts
{members}
      )
{drawing}    )'''


def document(parts, nets):
    return '(Source "DipTrace Schematic ASCII" "v45"\n  (Components\n' + "\n".join(parts) + '\n  )\n  (Nets\n' + "\n".join(nets) + '\n  )\n)\n'


class InspectorTests(unittest.TestCase):
    def inspect_text(self, source, *, strict_status=None):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "synthetic.asc"
            path.write_bytes(source.replace("\n", "\r\n").encode("cp1251"))
            result = inspector.inspect(path)
            if strict_status is not None:
                with patch("sys.argv", ["inspect", str(path), "--strict", "--json"]):
                    with contextlib.redirect_stdout(io.StringIO()):
                        self.assertEqual(inspector.main(), strict_status)
            return result

    def test_sparse_out_of_order_ids_and_multipart_refs(self):
        source = document(
            [part(41, ordinal=3, pin="A2", net=17), part(7, ordinal=1, pin="B1", net=17)],
            [net(17, [(7, 1), (41, 3)], geometry=True)],
        )
        result = self.inspect_text(source, strict_status=0)
        self.assertEqual([item.index for item in result["parts"]], [41, 7])
        self.assertEqual(result["nets"][0].index, 17)
        self.assertEqual(
            [(e.part_index, e.ref, e.string_number, e.part_name) for e in result["nets"][0].endpoints],
            [(7, "U1", "B1", "Unit B1"), (41, "U1", "A2", "Unit A2")],
        )
        self.assertEqual(result["unresolved_endpoints"], [])
        self.assertEqual(result["net_number_mismatches"], [])

    def test_contiguous_ids_and_unconnected_pin(self):
        result = self.inspect_text(document(
            [part(0, net=0), part(1, ref="U2", net=-1)], [net(0, [(0, 0)])],
        ), strict_status=0)
        self.assertEqual(result["nets"][0].endpoints[0].ref, "U1")
        self.assertEqual(result["net_number_mismatches"], [])

    def test_missing_part_id_does_not_use_nested_pin_number(self):
        with self.assertRaisesRegex(ValueError, "missing or invalid object Number"):
            self.inspect_text(document([part(None)], [net(4, [(1, 0)])]))

    def test_duplicate_part_ids_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate Part Number 2"):
            self.inspect_text(document([part(2), part(2, ref="U2")], [net(4, [(2, 0)])]))

    def test_duplicate_net_ids_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate Net Number 4"):
            self.inspect_text(document([part(2)], [net(4, [(2, 0)]), net(4, [])]))

    def test_unknown_part_id_fails_strict_resolution(self):
        result = self.inspect_text(document([part(2, net=-1)], [net(4, [(1, 0)])]), strict_status=1)
        self.assertEqual(result["unresolved_endpoints"][0]["part_index"], 1)

    def test_unknown_pin_ordinal_fails_strict_resolution(self):
        result = self.inspect_text(document([part(2, net=-1)], [net(4, [(2, 9)])]), strict_status=1)
        self.assertIsNone(result["unresolved_endpoints"][0]["string_number"])

    def test_pin_net_number_is_checked_against_explicit_net_id(self):
        result = self.inspect_text(document([part(2, net=5)], [net(4, [(2, 0)])]), strict_status=1)
        self.assertEqual(result["net_number_mismatches"][0]["declared"], [5])
        self.assertEqual(result["net_number_mismatches"][0]["resolved"], [4])


if __name__ == "__main__":
    unittest.main()
