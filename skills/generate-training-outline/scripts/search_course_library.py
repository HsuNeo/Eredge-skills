#!/usr/bin/env python3
"""只读检索课程库；不保存、不重算工作簿。需要已安装的 openpyxl。"""

import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import zipfile

import openpyxl


def read_bytes(path):
    """常规读取失败时，兼容 Office/OneDrive 的共享打开方式。"""
    try:
        return path.read_bytes()
    except PermissionError:
        if os.name != "nt":
            raise
        import ctypes
        from ctypes import wintypes
        import msvcrt

        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD,
                                      wintypes.DWORD, wintypes.LPVOID,
                                      wintypes.DWORD, wintypes.DWORD,
                                      wintypes.HANDLE]
        kernel.CreateFileW.restype = wintypes.HANDLE
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        # GENERIC_READ, FILE_SHARE_READ|WRITE|DELETE, OPEN_EXISTING.
        handle = kernel.CreateFileW(str(path.resolve()), 0x80000000, 7,
                                    None, 3, 0x80, None)
        if handle == wintypes.HANDLE(-1).value:
            raise ctypes.WinError(ctypes.get_last_error())
        try:
            descriptor = msvcrt.open_osfhandle(handle, os.O_RDONLY | os.O_BINARY)
        except Exception:
            kernel.CloseHandle(handle)
            raise
        with os.fdopen(descriptor, "rb") as stream:
            return stream.read()


def text(value):
    return json.dumps(str(value), ensure_ascii=False)


def nonempty_rows(sheet):
    # openpyxl 仅在合并区左上角返回值，不向其它行填充，避免重复时长。
    for row in sheet.iter_rows():
        cells = [(cell.coordinate, str(cell.value)) for cell in row
                 if cell.value is not None and str(cell.value).strip()]
        if cells:
            yield row[0].row, cells


def select_sheet(workbook, name):
    if name in workbook.sheetnames:
        return workbook[name]
    matches = [sheet for sheet in workbook
               if sheet.title.strip() == name.strip()]
    if not matches:
        raise ValueError(f"未找到工作表 {text(name)}；请先不带 --sheet 查看真实名称。")
    if len(matches) > 1:
        names = ", ".join(text(sheet.title) for sheet in matches)
        raise ValueError(f"去除首尾空格后名称有歧义：{names}；请使用完整真实名称。")
    return matches[0]


def keyword_hits(sheets, keyword):
    needle = keyword.casefold()
    for sheet in sheets:
        if needle in sheet.title.casefold():
            yield f"{text(sheet.title)}\t-\t-\t[工作表名称匹配] {text(sheet.title)}"
        for row_number, cells in nonempty_rows(sheet):
            for coordinate, value in cells:
                if needle in value.casefold():
                    yield f"{text(sheet.title)}\t{row_number}\t{coordinate}\t{text(value)}"


def limited_output(records, limit):
    total = 0
    for total, record in enumerate(records, 1):
        if total <= limit:
            print(record)
    shown = min(total, limit)
    print(f"共 {total} 条，已显示 {shown} 条。")
    if total > limit:
        print(f"已截断 {total - limit} 条；增大 --limit 可继续查看。")
    return total, shown


def inspect_file(path, sheet_name=None, keyword=None, limit=50):
    if path.suffix.lower() != ".xlsx":
        raise ValueError("只支持 .xlsx；Word 文档请使用文档技能。")
    content = read_bytes(path)
    # 普通内存模式用于读取合并范围；仅载入，不调用 save 或计算公式。
    workbook = openpyxl.load_workbook(io.BytesIO(content), data_only=False,
                                     keep_links=False)
    try:
        sheets = [select_sheet(workbook, sheet_name)] if sheet_name is not None else list(workbook)
        print(f"文件：{path.resolve()}")
        print("只读；公式显示原公式；合并区只显示左上角原值。")
        if keyword is not None:
            print("工作表\t行号\t单元格\t内容")
            limited_output(keyword_hits(sheets, keyword), limit)
        elif sheet_name is not None:
            sheet = sheets[0]
            print(f"工作表：{text(sheet.title)}")
            records = (f"第 {number} 行\t" + " | ".join(
                f"{coordinate}={text(value)}" for coordinate, value in cells)
                for number, cells in nonempty_rows(sheet))
            limited_output(records, limit)
        else:
            print(f"共 {len(sheets)} 个工作表；以下名称保留首尾空格。")
            for sheet in sheets:
                print(f"\n工作表：{text(sheet.title)}；行={sheet.max_row}；"
                      f"列={sheet.max_column}；合并范围={len(sheet.merged_cells.ranges)}")
                for index, (number, cells) in enumerate(nonempty_rows(sheet)):
                    if index == 3:
                        break
                    print(f"  第 {number} 行：" + " | ".join(
                        f"{coordinate}={text(value)}" for coordinate, value in cells))
    finally:
        workbook.close()


def self_test():
    from contextlib import redirect_stdout
    from unittest.mock import patch

    with tempfile.TemporaryDirectory(prefix="course-library-check-") as directory:
        path = Path(directory) / "课程库.xlsx"
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "公路课程 "
        sheet.append(["时长", "课程内容"])
        sheet.append([3, "路基计量案例"])
        sheet.append([None, "桥梁计量案例"])
        sheet.merge_cells("A2:A3")
        workbook.create_sheet("对照")
        workbook.create_sheet("对照 ")
        workbook.save(path)
        original = path.read_bytes()
        before = hashlib.sha256(original).digest()
        if os.name == "nt":
            with patch.object(Path, "read_bytes", side_effect=PermissionError("模拟共享文件")):
                assert read_bytes(path) == original
        assert select_sheet(workbook, "公路课程").title == "公路课程 "
        assert select_sheet(workbook, "对照").title == "对照"
        try:
            select_sheet(workbook, " 对照")
        except ValueError as error:
            assert "歧义" in str(error)
        else:
            raise AssertionError("应报告去空格名称歧义")
        rows = list(nonempty_rows(sheet))
        assert sum(value == "3" for _, cells in rows for _, value in cells) == 1
        hits = list(keyword_hits([sheet], "计量"))
        assert len(hits) == 2 and "\t2\tB2\t" in hits[0] and "\t3\tB3\t" in hits[1]
        assert "[工作表名称匹配]" in next(keyword_hits([sheet], "公路课程"))
        captured = io.StringIO()
        with redirect_stdout(captured):
            inspect_file(path, "公路课程", "计量", 1)
        assert "已截断 1 条" in captured.getvalue()
        assert "B2" in captured.getvalue() and "B3" not in captured.getvalue()
        assert hashlib.sha256(path.read_bytes()).digest() == before
        workbook.close()
    print("自检通过：合并值不重复、源文件未改、名称空格/歧义、关键词坐标、截断提示、共享读取。")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", type=Path, help="课程库 .xlsx 路径")
    parser.add_argument("--keyword", help="按单元格内容或表名搜索；不区分英文大小写")
    parser.add_argument("--sheet", help="展开工作表；可与 --keyword 一起限定检索范围")
    parser.add_argument("--limit", type=int, default=50, help="最多显示的命中条数/展开行数，默认 50")
    parser.add_argument("--self-test", action="store_true", help="在临时小工作簿上运行自检")
    args = parser.parse_args()
    if args.file is None and not args.self_test:
        parser.error('请用 --file 指定课程库路径')
    if args.limit < 1:
        parser.error("--limit 必须大于 0")
    if args.keyword is not None and not args.keyword.strip():
        parser.error("--keyword 不能为空")
    try:
        if args.self_test:
            self_test()
        else:
            inspect_file(args.file, args.sheet, args.keyword, args.limit)
    except (OSError, ValueError, zipfile.BadZipFile,
            openpyxl.utils.exceptions.InvalidFileException) as error:
        print(f"读取失败：{error}", file=sys.stderr)
        print("请检查路径和文件权限；若正在同步或被独占，请另存临时副本后用 --file 指向副本。",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
