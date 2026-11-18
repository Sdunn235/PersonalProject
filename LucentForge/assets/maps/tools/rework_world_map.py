from __future__ import annotations

from collections import Counter
from pathlib import Path
import csv
import math
import zipfile
from xml.sax.saxutils import escape

SIZE = 512
ROOT = Path(r"C:/Users/Shawn/Documents/Workspace/Personal Project/LucentForge")
CSV_PATH = ROOT / "assets" / "maps" / "world_map.csv"
XLSX_PATH = ROOT / "assets" / "maps" / "world_map_visual_aid.xlsx"

TOKEN_INFO = {
    "O": ("Ocean", "Deep water / open sea", "1E3A5F", True),
    "C": ("Coast", "Shoreline and shallow edge tiles", "D9C48A", False),
    "B": ("Bluff", "Steep coastal escarpment / cliff", "8E6B4F", True),
    "R": ("River", "Major inland river or channel", "3B82F6", True),
    "W": ("Wetland", "Marsh / floodplain / lake edge", "65A30D", False),
    "V": ("Valley", "Fertile mountain valley", "A3E635", False),
    "P": ("Plains", "Open temperate lowlands", "86EFAC", False),
    "F": ("Forest", "Dense woodland or temperate forest", "166534", True),
    "S": ("Savannah", "Open warm grassland", "FDE68A", False),
    "D": ("Drylands", "Desert / scrub / badlands", "F59E0B", False),
    "J": ("Jungle", "Hot, wet tropical growth", "0F766E", True),
    "H": ("Highlands", "Foothills / plateaus / uplands", "A78BFA", True),
    "M": ("Mountains", "Major mountain massifs and peaks", "64748B", True),
    "I": ("Ice", "Polar ice cap / frozen sea", "E2E8F0", False),
}

LAND = set("CBRWVPFSDJHMI")
CORE_LAND = set("BVPFSDJHMI")


def wrap_dx(x: int, center: int) -> int:
    d = abs(x - center)
    return min(d, SIZE - d)


def ellipse(x: int, y: int, cx: int, cy: int, rx: float, ry: float) -> float:
    dx = wrap_dx(x, cx)
    dy = y - cy
    return (dx * dx) / (rx * rx) + (dy * dy) / (ry * ry)


def to_grid() -> list[list[str]]:
    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    if len(rows) != SIZE or len(rows[0]) != SIZE:
        raise ValueError(f"Expected {SIZE}x{SIZE}, got {len(rows)}x{len(rows[0])}")
    return rows


def carve_oceans(grid: list[list[str]]) -> None:
    # Force visible globe-scale separation with three ocean corridors.
    for y in range(SIZE):
        for x in range(SIZE):
            e1 = ellipse(x, y, 256, 252, 54.0, 205.0)  # central meridian ocean
            e2 = ellipse(x, y, 146, 220, 44.0, 150.0)  # western ocean arm
            e3 = ellipse(x, y, 384, 214, 48.0, 155.0)  # eastern ocean arm
            e4 = ellipse(x, y, 310, 330, 70.0, 36.0)   # inland sea basin
            if e1 < 1.0 or e2 < 1.0 or e3 < 1.0 or e4 < 1.0:
                grid[y][x] = "O"


def add_archipelagos(grid: list[list[str]]) -> None:
    # Two fantasy island belts to make the map visibly less section-like.
    for i in range(18):
        cx = (28 + i * 28) % SIZE
        cy = 174 + int(12.0 * math.sin(i * 0.65))
        for y in range(max(0, cy - 6), min(SIZE, cy + 7)):
            for x in range(cx - 8, cx + 9):
                xx = x % SIZE
                d = ellipse(xx, y, cx, cy, 7.0, 4.5)
                if d < 1.0:
                    grid[y][xx] = "C" if d > 0.45 else ("H" if i % 3 == 0 else "F")

    for i in range(16):
        cx = (10 + i * 32) % SIZE
        cy = 308 + int(14.0 * math.cos(i * 0.55))
        for y in range(max(0, cy - 7), min(SIZE, cy + 8)):
            for x in range(cx - 9, cx + 10):
                xx = x % SIZE
                d = ellipse(xx, y, cx, cy, 8.0, 5.0)
                if d < 1.0:
                    grid[y][xx] = "C" if d > 0.52 else ("J" if i % 4 == 0 else "F")


def apply_coasts(grid: list[list[str]]) -> None:
    updates: list[tuple[int, int, str]] = []
    for y in range(SIZE):
        for x in range(SIZE):
            token = grid[y][x]
            if token not in LAND:
                continue
            touches_ocean = False
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx = (x + dx) % SIZE
                ny = y + dy
                if ny < 0 or ny >= SIZE:
                    continue
                if grid[ny][nx] == "O":
                    touches_ocean = True
                    break
            if touches_ocean:
                if token in {"M", "H"}:
                    updates.append((x, y, "B"))
                elif token != "R":
                    updates.append((x, y, "C"))
    for x, y, t in updates:
        grid[y][x] = t


def enforce_climate_bands(grid: list[list[str]]) -> None:
    # Make biome bands more Earth-like but keep fantasy features.
    for y in range(SIZE):
        lat = abs((y - ((SIZE - 1) / 2.0)) / ((SIZE - 1) / 2.0))
        for x in range(SIZE):
            t = grid[y][x]
            if t in {"O", "R", "C", "B", "W", "V"}:
                continue
            if lat > 0.92:
                grid[y][x] = "I"
            elif lat < 0.20 and t in {"F", "P", "S", "D"}:
                grid[y][x] = "J" if (x + y) % 5 else "F"
            elif 0.20 <= lat < 0.38 and t in {"J", "P", "F", "D"}:
                grid[y][x] = "S" if (x * 3 + y) % 7 < 3 else "F"
            elif 0.38 <= lat < 0.70 and t in {"J", "D"}:
                grid[y][x] = "P" if (x + y) % 3 else "F"
            elif lat >= 0.70 and t in {"J", "S", "D", "P", "F"}:
                grid[y][x] = "F" if (x + y) % 4 else "H"


def write_csv(grid: list[list[str]]) -> None:
    with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(grid)


# --- Minimal XLSX builder ---------------------------------------------------

def col_letter(index: int) -> str:
    s = ""
    while index:
        index, rem = divmod(index - 1, 26)
        s = chr(65 + rem) + s
    return s


def xml_cell(ref: str, value: str, style: int) -> str:
    return f'<c r="{ref}" t="inlineStr" s="{style}"><is><t>{escape(value)}</t></is></c>'


def build_styles() -> tuple[str, dict[str, int]]:
    fills = [
        '<fill><patternFill patternType="none"/></fill>',
        '<fill><patternFill patternType="gray125"/></fill>',
        '<fill><patternFill patternType="solid"><fgColor rgb="D9EAF7"/><bgColor indexed="64"/></patternFill></fill>',
    ]
    fonts = [
        '<font><sz val="10"/><color rgb="000000"/><name val="Calibri"/></font>',
        '<font><b/><sz val="10"/><color rgb="000000"/><name val="Calibri"/></font>',
        '<font><sz val="10"/><color rgb="FFFFFF"/><name val="Calibri"/></font>',
    ]
    borders = [
        '<border><left/><right/><top/><bottom/><diagonal/></border>',
        '<border><left style="thin"><color rgb="D1D5DB"/></left><right style="thin"><color rgb="D1D5DB"/></right><top style="thin"><color rgb="D1D5DB"/></top><bottom style="thin"><color rgb="D1D5DB"/></bottom><diagonal/></border>',
    ]

    token_fill = {}
    for token, (_, _, color, _) in TOKEN_INFO.items():
        fills.append(f'<fill><patternFill patternType="solid"><fgColor rgb="{color}"/><bgColor indexed="64"/></patternFill></fill>')
        token_fill[token] = len(fills) - 1

    style_ids = {"default": 0, "header": 1}
    for i, token in enumerate(TOKEN_INFO.keys()):
        style_ids[token] = 2 + i

    cell_xfs = [
        '<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>',
        '<xf numFmtId="0" fontId="1" fillId="2" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="center" vertical="center"/></xf>',
    ]
    for token, (_, _, _, white_text) in TOKEN_INFO.items():
        fid = 2 if white_text else 0
        cell_xfs.append(
            f'<xf numFmtId="0" fontId="{fid}" fillId="{token_fill[token]}" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="center" vertical="center"/></xf>'
        )

    xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f'<fonts count="{len(fonts)}">' + ''.join(fonts) + '</fonts>'
        f'<fills count="{len(fills)}">' + ''.join(fills) + '</fills>'
        f'<borders count="{len(borders)}">' + ''.join(borders) + '</borders>'
        '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
        f'<cellXfs count="{len(cell_xfs)}">' + ''.join(cell_xfs) + '</cellXfs>'
        '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>'
        '</styleSheet>'
    )
    return xml, style_ids


def build_map_sheet(grid: list[list[str]], style_ids: dict[str, int]) -> str:
    row_xml = []
    for r_idx, row in enumerate(grid, start=1):
        cells = [xml_cell(f"{col_letter(c_idx)}{r_idx}", token, style_ids[token]) for c_idx, token in enumerate(row, start=1)]
        row_xml.append(f'<row r="{r_idx}" ht="15" customHeight="1">{"".join(cells)}</row>')
    cols_xml = ''.join(f'<col min="{i}" max="{i}" width="2.2" customWidth="1"/>' for i in range(1, SIZE + 1))
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        f'<dimension ref="A1:{col_letter(SIZE)}{SIZE}"/>'
        '<sheetViews><sheetView workbookViewId="0" showGridLines="0"/></sheetViews>'
        '<sheetFormatPr defaultRowHeight="15"/>'
        f'<cols>{cols_xml}</cols>'
        '<sheetData>' + ''.join(row_xml) + '</sheetData>'
        '<pageMargins left="0.1" right="0.1" top="0.1" bottom="0.1" header="0.3" footer="0.3"/>'
        '</worksheet>'
    )


def build_legend_sheet(style_ids: dict[str, int]) -> str:
    headers = ["Token", "Meaning", "Notes", "Color"]
    rows = []
    hcells = [xml_cell(f"{col_letter(i)}1", h, style_ids["header"]) for i, h in enumerate(headers, start=1)]
    rows.append(f'<row r="1" ht="18" customHeight="1">{"".join(hcells)}</row>')
    for r_idx, (token, (name, notes, color, _)) in enumerate(TOKEN_INFO.items(), start=2):
        cells = [
            xml_cell(f"A{r_idx}", token, style_ids[token]),
            xml_cell(f"B{r_idx}", name, style_ids["default"]),
            xml_cell(f"C{r_idx}", notes, style_ids["default"]),
            xml_cell(f"D{r_idx}", color, style_ids["default"]),
        ]
        rows.append(f'<row r="{r_idx}" ht="18" customHeight="1">{"".join(cells)}</row>')
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<dimension ref="A1:D15"/>'
        '<sheetViews><sheetView workbookViewId="0"/></sheetViews>'
        '<sheetFormatPr defaultRowHeight="18"/>'
        '<cols><col min="1" max="1" width="10" customWidth="1"/><col min="2" max="2" width="18" customWidth="1"/><col min="3" max="3" width="42" customWidth="1"/><col min="4" max="4" width="12" customWidth="1"/></cols>'
        '<sheetData>' + ''.join(rows) + '</sheetData>'
        '<pageMargins left="0.1" right="0.1" top="0.1" bottom="0.1" header="0.3" footer="0.3"/>'
        '</worksheet>'
    )


def build_notes_sheet() -> str:
    notes = [
        "World map visual aid regenerated with stronger visible macro changes.",
        "This pass carved three major ocean corridors plus a large inland sea.",
        "Added two island belts to make the globe read less like one central section.",
        f"Source CSV: {CSV_PATH}",
    ]
    rows = [f'<row r="{i}" ht="18" customHeight="1"><c r="A{i}" t="inlineStr" s="0"><is><t>{escape(text)}</t></is></c></row>' for i, text in enumerate(notes, start=1)]
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<dimension ref="A1:A4"/>'
        '<sheetViews><sheetView workbookViewId="0"/></sheetViews>'
        '<sheetFormatPr defaultRowHeight="18"/>'
        '<cols><col min="1" max="1" width="120" customWidth="1"/></cols>'
        '<sheetData>' + ''.join(rows) + '</sheetData>'
        '<pageMargins left="0.1" right="0.1" top="0.1" bottom="0.1" header="0.3" footer="0.3"/>'
        '</worksheet>'
    )


def write_xlsx(grid: list[list[str]]) -> None:
    styles_xml, style_ids = build_styles()
    map_xml = build_map_sheet(grid, style_ids)
    legend_xml = build_legend_sheet(style_ids)
    notes_xml = build_notes_sheet()

    workbook_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<sheets>'
        '<sheet name="World Map" sheetId="1" r:id="rId1"/>'
        '<sheet name="Legend" sheetId="2" r:id="rId2"/>'
        '<sheet name="Notes" sheetId="3" r:id="rId3"/>'
        '</sheets></workbook>'
    )
    workbook_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet2.xml"/>'
        '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet3.xml"/>'
        '<Relationship Id="rId4" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
        '</Relationships>'
    )
    root_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
        '</Relationships>'
    )
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
        '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        '<Override PartName="/xl/worksheets/sheet2.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        '<Override PartName="/xl/worksheets/sheet3.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        '</Types>'
    )

    with zipfile.ZipFile(XLSX_PATH, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", root_rels)
        zf.writestr("xl/workbook.xml", workbook_xml)
        zf.writestr("xl/_rels/workbook.xml.rels", workbook_rels)
        zf.writestr("xl/styles.xml", styles_xml)
        zf.writestr("xl/worksheets/sheet1.xml", map_xml)
        zf.writestr("xl/worksheets/sheet2.xml", legend_xml)
        zf.writestr("xl/worksheets/sheet3.xml", notes_xml)


def main() -> None:
    grid = to_grid()

    carve_oceans(grid)
    add_archipelagos(grid)
    apply_coasts(grid)
    enforce_climate_bands(grid)

    write_csv(grid)
    write_xlsx(grid)

    counts = Counter()
    for row in grid:
        counts.update(row)

    print(f"Wrote {CSV_PATH}")
    print(f"Wrote {XLSX_PATH}")
    for token, count in sorted(counts.items()):
        print(f"  {token}: {count}")


if __name__ == "__main__":
    main()
