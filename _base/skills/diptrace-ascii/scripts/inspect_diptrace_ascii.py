#!/usr/bin/env python3
"""Read-only structural inspector for DipTrace Schematic ASCII files."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Iterable


CYRILLIC_RE = re.compile(r"[\u0400-\u04ff]")
PART_START_RE = re.compile(
    r'^\s+\(Part\s+"((?:[^"\\]|\\.)*)"\s+"((?:[^"\\]|\\.)*)"'
)
NET_START_RE = re.compile(r'^\s+\(Net\s+"((?:[^"\\]|\\.)*)"')
PIN_START_RE = re.compile(r"^\s+\(Pin\s+(-?\d+)\b")
PAD_RE = re.compile(r'^\s+\(Pad\s+(-?\d+)\s+"([^"]*)"')
ENDPOINT_RE = re.compile(r"^\s+\(pt\s+(-?\d+)\s+(-?\d+)\s*\)\s*$")
FIELD_RE = re.compile(r"^\s*\(([A-Za-z_][A-Za-z0-9_]*)\b")


@dataclass
class Pin:
    ordinal: int
    number: str | None
    string_number: str | None
    name: str | None
    net_number: int | None


@dataclass
class Part:
    index: int
    line: int
    library_name: str
    ref: str
    value: str | None
    base_name: str | None
    part_name: str | None
    pins: list[Pin]
    pad_numbers: list[str]


@dataclass
class Endpoint:
    part_index: int
    pin_ordinal: int
    ref: str | None
    part_name: str | None
    string_number: str | None
    pin_name: str | None


@dataclass
class Net:
    index: int
    line: int
    name: str
    endpoint_pairs: list[tuple[int, int]]
    endpoints: list[Endpoint]


def decode_bytes(data: bytes) -> tuple[str, str, str]:
    if data.startswith(b"\xef\xbb\xbf"):
        return data.decode("utf-8-sig"), "utf-8-sig", "UTF-8"
    if data.startswith(b"\xff\xfe"):
        return data.decode("utf-16-le"), "utf-16-le", "UTF-16LE"
    if data.startswith(b"\xfe\xff"):
        return data.decode("utf-16-be"), "utf-16-be", "UTF-16BE"
    try:
        return data.decode("utf-8"), "utf-8", "none"
    except UnicodeDecodeError:
        return data.decode("cp1251"), "cp1251", "none"


def newline_summary(text: str) -> dict[str, Any]:
    crlf = text.count("\r\n")
    lf_only = len(re.findall(r"(?<!\r)\n", text))
    cr_only = len(re.findall(r"\r(?!\n)", text))
    kinds = sum(value > 0 for value in (crlf, lf_only, cr_only))
    if kinds == 0:
        style = "none"
    elif kinds > 1:
        style = "mixed"
    elif crlf:
        style = "CRLF"
    elif lf_only:
        style = "LF"
    else:
        style = "CR"
    return {"style": style, "crlf": crlf, "lf_only": lf_only, "cr_only": cr_only}


def scan_parentheses(text: str) -> dict[str, Any]:
    depth = 0
    minimum = 0
    opens = 0
    closes = 0
    in_string = False
    escaped = False
    for char in text:
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "(":
            depth += 1
            opens += 1
        elif char == ")":
            depth -= 1
            closes += 1
            minimum = min(minimum, depth)
    return {
        "open": opens,
        "close": closes,
        "final_depth": depth,
        "minimum_depth": minimum,
        "unterminated_string": in_string,
        "valid": depth == 0 and minimum >= 0 and not in_string,
    }


def paren_delta(line: str) -> int:
    return scan_parentheses(line)["final_depth"]


def iter_blocks(lines: list[str], start_re: re.Pattern[str]) -> Iterable[tuple[int, re.Match[str], list[str]]]:
    index = 0
    while index < len(lines):
        match = start_re.match(lines[index])
        if not match:
            index += 1
            continue
        start = index
        balance = paren_delta(lines[index])
        index += 1
        while index < len(lines) and balance > 0:
            balance += paren_delta(lines[index])
            index += 1
        yield start, match, lines[start:index]


def quoted_field(block: str, name: str) -> str | None:
    pattern = re.compile(
        rf'^\s+\({re.escape(name)}\s+"((?:[^"\\]|\\.)*)"\)', re.MULTILINE
    )
    match = pattern.search(block)
    return match.group(1) if match else None


def integer_field(block: str, name: str) -> int | None:
    match = re.search(rf"^\s+\({re.escape(name)}\s+(-?\d+)\)", block, re.MULTILINE)
    return int(match.group(1)) if match else None


def object_number(block_lines: list[str]) -> int:
    """Read the object's own Number, never a nested pin/pad Number."""
    depth = paren_delta(block_lines[0])
    for line in block_lines[1:]:
        if depth == 1:
            match = re.fullmatch(r"\s*\(Number\s+(\d+)\)\s*", line)
            if match:
                return int(match.group(1))
        depth += paren_delta(line)
    raise ValueError(f"missing or invalid object Number: {block_lines[0].strip()}")


def parse_pins(block_lines: list[str]) -> list[Pin]:
    pins: list[Pin] = []
    for _, match, pin_lines in iter_blocks(block_lines, PIN_START_RE):
        block = "\n".join(pin_lines)
        numeric = integer_field(block, "Number")
        pins.append(
            Pin(
                ordinal=int(match.group(1)),
                number=str(numeric) if numeric is not None else None,
                string_number=quoted_field(block, "StringNumber"),
                name=quoted_field(block, "Name"),
                net_number=integer_field(block, "NetNumber"),
            )
        )
    return pins


def parse_parts(lines: list[str]) -> list[Part]:
    parts: list[Part] = []
    numbers: set[int] = set()
    for start, match, block_lines in iter_blocks(lines, PART_START_RE):
        block = "\n".join(block_lines)
        number = object_number(block_lines)
        if number in numbers:
            raise ValueError(f"duplicate Part Number {number} at line {start + 1}")
        numbers.add(number)
        parts.append(
            Part(
                index=number,
                line=start + 1,
                library_name=match.group(1),
                ref=match.group(2),
                value=quoted_field(block, "Value"),
                base_name=quoted_field(block, "BaseName"),
                part_name=quoted_field(block, "PartName"),
                pins=parse_pins(block_lines),
                pad_numbers=[m.group(2) for line in block_lines if (m := PAD_RE.match(line))],
            )
        )
    return parts


def parse_nets(lines: list[str], parts: list[Part]) -> list[Net]:
    nets: list[Net] = []
    parts_by_number = {part.index: part for part in parts}
    numbers: set[int] = set()
    for start, match, block_lines in iter_blocks(lines, NET_START_RE):
        number = object_number(block_lines)
        if number in numbers:
            raise ValueError(f"duplicate Net Number {number} at line {start + 1}")
        numbers.add(number)
        pairs = [
            (int(m.group(1)), int(m.group(2)))
            for _, _, member_lines in iter_blocks(block_lines, re.compile(r"^\s+\(Parts\s*$"))
            for line in member_lines
            if (m := ENDPOINT_RE.match(line))
        ]
        endpoints: list[Endpoint] = []
        for part_index, pin_ordinal in pairs:
            part = parts_by_number.get(part_index)
            pin = None
            if part:
                pin = next((candidate for candidate in part.pins if candidate.ordinal == pin_ordinal), None)
            endpoints.append(
                Endpoint(
                    part_index=part_index,
                    pin_ordinal=pin_ordinal,
                    ref=part.ref if part else None,
                    part_name=part.part_name if part else None,
                    string_number=pin.string_number if pin else None,
                    pin_name=pin.name if pin else None,
                )
            )
        nets.append(Net(index=number, line=start + 1, name=match.group(1), endpoint_pairs=pairs, endpoints=endpoints))
    return nets


def line_scope(line_index: int, part_ranges: list[tuple[int, int]], cache_start: int | None) -> str:
    if any(start <= line_index < end for start, end in part_ranges):
        return "component"
    if cache_start is not None and line_index >= cache_start:
        return "cache"
    return "document"


def inspect(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    text, encoding, bom = decode_bytes(data)
    lines = text.splitlines()
    structure = scan_parentheses(text)
    parts = parse_parts(lines)
    nets = parse_nets(lines, parts)
    part_ranges = [
        (start, start + len(block)) for start, _, block in iter_blocks(lines, PART_START_RE)
    ]
    cache_start = next((i for i, line in enumerate(lines) if re.match(r"^\s*\(CacheLib\b", line)), None)
    cyrillic: list[dict[str, Any]] = []
    for index, line in enumerate(lines):
        if not CYRILLIC_RE.search(line):
            continue
        field_match = FIELD_RE.match(line)
        cyrillic.append(
            {
                "line": index + 1,
                "scope": line_scope(index, part_ranges, cache_start),
                "field": field_match.group(1) if field_match else None,
                "text": line.strip(),
            }
        )
    unresolved = [asdict(endpoint) for net in nets for endpoint in net.endpoints if endpoint.ref is None or endpoint.string_number is None]
    memberships: dict[tuple[int, int], list[int]] = {}
    for net in nets:
        for pair in net.endpoint_pairs:
            memberships.setdefault(pair, []).append(net.index)
    net_number_mismatches = []
    for part in parts:
        for pin in part.pins:
            expected = [] if pin.net_number == -1 else [pin.net_number]
            actual = memberships.get((part.index, pin.ordinal), [])
            if expected != actual:
                net_number_mismatches.append({
                    "part_index": part.index, "ref": part.ref,
                    "pin_ordinal": pin.ordinal, "declared": expected, "resolved": actual,
                })
    return {
        "path": str(path.resolve()),
        "sha256": hashlib.sha256(data).hexdigest().upper(),
        "bytes": len(data),
        "encoding": encoding,
        "bom": bom,
        "newlines": newline_summary(text),
        "lines": len(lines),
        "structure": structure,
        "parts": parts,
        "nets": nets,
        "cyrillic": cyrillic,
        "unresolved_endpoints": unresolved,
        "net_number_mismatches": net_number_mismatches,
    }


def connectivity_signature(result: dict[str, Any]) -> dict[str, Any]:
    parts: list[Part] = result["parts"]
    nets: list[Net] = result["nets"]
    return {
        "parts": [
            {
                "index": part.index,
                "ref": part.ref,
                "part_name": part.part_name,
                "pins": [(pin.ordinal, pin.string_number, pin.name) for pin in part.pins],
                "pads": part.pad_numbers,
            }
            for part in parts
        ],
        "nets": [(net.index, net.name, net.endpoint_pairs) for net in nets],
    }


def serialize(result: dict[str, Any]) -> dict[str, Any]:
    converted = dict(result)
    converted["parts"] = [asdict(item) for item in result["parts"]]
    converted["nets"] = [asdict(item) for item in result["nets"]]
    return converted


def print_part(part: Part) -> None:
    print(f"\nREF {part.ref}  index={part.index} line={part.line} part={part.part_name!r}")
    print(f"  library={part.library_name!r} value={part.value!r} base={part.base_name!r}")
    print(f"  pads({len(part.pad_numbers)}): {', '.join(part.pad_numbers) or '-'}")
    for pin in part.pins:
        print(
            f"  pin ordinal={pin.ordinal} string={pin.string_number!r} "
            f"name={pin.name!r} net_number={pin.net_number}"
        )


def print_net(net: Net) -> None:
    print(f"\nNET {net.name!r}  index={net.index} line={net.line} endpoints={len(net.endpoints)}")
    for endpoint in net.endpoints:
        label = endpoint.ref or f"part-index:{endpoint.part_index}"
        pin = endpoint.string_number or f"ordinal:{endpoint.pin_ordinal}"
        suffix = f" [{endpoint.pin_name}]" if endpoint.pin_name else ""
        unit = f" ({endpoint.part_name})" if endpoint.part_name else ""
        print(f"  {label}.{pin}{suffix}{unit}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path, help="DipTrace Schematic ASCII file")
    parser.add_argument("--ref", action="append", default=[], help="show every placed part with this reference")
    parser.add_argument("--net", action="append", default=[], help="show a named net and resolved endpoints")
    parser.add_argument("--compare", type=Path, help="pre-edit file whose connectivity must match")
    parser.add_argument("--json", action="store_true", help="emit the full inspection result as JSON")
    parser.add_argument("--show-cyrillic", action="store_true", help="show every line containing Cyrillic")
    parser.add_argument("--strict", action="store_true", help="return nonzero for structural or resolution failures")
    return parser


def main() -> int:
    if sys.platform == "win32":
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    args = build_parser().parse_args()
    if not args.file.is_file():
        print(f"error: file not found: {args.file}", file=sys.stderr)
        return 2
    result = inspect(args.file)
    compare_changed = False
    if args.compare:
        if not args.compare.is_file():
            print(f"error: comparison file not found: {args.compare}", file=sys.stderr)
            return 2
        baseline = inspect(args.compare)
        compare_changed = connectivity_signature(result) != connectivity_signature(baseline)
        result["comparison"] = {
            "path": str(args.compare.resolve()),
            "sha256": baseline["sha256"],
            "connectivity_equal": not compare_changed,
            "encoding_equal": result["encoding"] == baseline["encoding"],
            "newline_style_equal": result["newlines"]["style"] == baseline["newlines"]["style"],
        }
    if args.json:
        print(json.dumps(serialize(result), ensure_ascii=False, indent=2))
    else:
        print(f"File: {result['path']}")
        print(f"SHA-256: {result['sha256']}  bytes={result['bytes']} lines={result['lines']}")
        print(
            f"Encoding: {result['encoding']}  BOM={result['bom']}  "
            f"newlines={result['newlines']['style']}"
        )
        print(
            f"Structure: valid={result['structure']['valid']} "
            f"depth={result['structure']['final_depth']} min={result['structure']['minimum_depth']}"
        )
        print(
            f"Placed parts: {len(result['parts'])}  nets: {len(result['nets'])}  "
            f"unresolved endpoints: {len(result['unresolved_endpoints'])}  "
            f"net-number mismatches: {len(result['net_number_mismatches'])}  "
            f"Cyrillic lines: {len(result['cyrillic'])}"
        )
        if args.compare:
            comparison = result["comparison"]
            print(
                f"Compare: connectivity_equal={comparison['connectivity_equal']} "
                f"encoding_equal={comparison['encoding_equal']} "
                f"newline_style_equal={comparison['newline_style_equal']}"
            )
        if args.show_cyrillic:
            for item in result["cyrillic"]:
                print(
                    f"CYRILLIC line={item['line']} scope={item['scope']} "
                    f"field={item['field']}: {item['text']}"
                )
        for ref in args.ref:
            matches = [part for part in result["parts"] if part.ref == ref]
            if not matches:
                print(f"\nREF {ref}: not found")
            for part in matches:
                print_part(part)
        for requested_net in args.net:
            matches = [net for net in result["nets"] if net.name == requested_net]
            if not matches:
                print(f"\nNET {requested_net!r}: not found")
            for net in matches:
                print_net(net)
    strict_failure = (
        not result["structure"]["valid"]
        or not result["parts"]
        or not result["nets"]
        or bool(result["unresolved_endpoints"])
        or bool(result["net_number_mismatches"])
        or compare_changed
    )
    return 1 if args.strict and strict_failure else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(2)
