#!/usr/bin/env python3
# fucksql.py — SBSQL 本地管理端
# 用法：python fucksql.py
# 依赖：无（纯标准库）

import os
import re
import sys

class SBSQL:
    def __init__(self, root_dir="data"):
        self.root = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), root_dir))
        if not os.path.exists(self.root):
            raise ValueError("ERROR 1049 (42000): Database root directory does not exist")

    def _validate(self, value, name):
        if not isinstance(value, str) or not value:
            raise ValueError(f"ERROR 1136 (21S01): {name} cannot be empty")
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise ValueError(f"ERROR 1142 (42000): {name} contains invalid characters for SBSQL")
        return value

    def _secure_path(self, table, item):
        table_dir = os.path.join(self.root, table)
        table_dir = os.path.realpath(table_dir)
        if not table_dir.startswith(self.root):
            raise ValueError("ERROR 1045 (28000): Access denied for path traversal attempt")
        item_file = os.path.join(table_dir, item + ".txt")
        item_file = os.path.realpath(item_file)
        if not item_file.startswith(self.root):
            raise ValueError("ERROR 1045 (28000): Access denied for path traversal attempt")
        return item_file

    def scan_tables(self):
        tables = []
        for dir_name in os.listdir(self.root):
            if os.path.isdir(os.path.join(self.root, dir_name)):
                tables.append(dir_name)
        return tables

    def scan_headers(self, table):
        table = self._validate(table, "Table name")
        table_dir = os.path.join(self.root, table)
        table_dir = os.path.realpath(table_dir)
        if not table_dir.startswith(self.root):
            raise ValueError("ERROR 1045 (28000): Access denied")
        if not os.path.exists(table_dir):
            return {"status": "error", "message": "ERROR 1146 (42S02): Table does not exist"}
        headers = []
        for filename in os.listdir(table_dir):
            if not filename.startswith("_"):
                headers.append(filename)
        return headers

    def get(self, table, item, index=0):
        table = self._validate(table, "Table name")
        item = self._validate(item, "Column name")
        index = int(index)
        if index < 0:
            raise ValueError("ERROR 1210 (HY000): Invalid argument for row index")
        safe_path = self._secure_path(table, item)
        if not os.path.exists(safe_path):
            return {"status": "error", "message": "ERROR 1054 (42S22): Unknown column"}
        with open(safe_path, 'r') as f:
            lines = f.readlines()
            if index >= len(lines):
                return {"status": "error", "message": f"ERROR 1096 (HY000): No data at row {index}"}
            return {"status": "ok", "data": lines[index].strip()}


PROMPT = "SBSQL [(none)]> "
WRITE_CMDS = {"INSERT","UPDATE","DELETE","DROP","CREATE","ALTER","TRUNCATE","REPLACE","GRANT","REVOKE"}


def read_input():
    try:
        raw = input(PROMPT)
    except (EOFError, KeyboardInterrupt):
        return None
    if not raw.strip():
        return ""
    first = raw.strip().split()[0].upper() if raw.strip().split() else ""
    if first in WRITE_CMDS:
        sys.stdout.write("\033[2K\r")
        sys.stdout.write(PROMPT + raw.rstrip().rstrip(";").rstrip() + "\n")
        sys.stdout.write("ERROR 1064 (42000): You have an error in your SQL syntax; check the manual that corresponds to your SBSQL server version for the right syntax to use near '' at end of line\n")
        sys.stdout.flush()
        return ""
    return raw


def print_banner():
    print("""Welcome to the SBSQL monitor.  Commands end with ; or \\g.
Your SBSQL connection id is 1
Server version: 1.0.0 SBSQL Community Edition (ReadOnly)

Copyright (c) 2024-2026 SBSQL Corp.
Type 'help;' or '\\h' for help. Type '\\c' to clear the buffer.
""")


def main():
    try:
        sbsql = SBSQL()
    except ValueError as e:
        print(e)
        sys.exit(1)

    print_banner()

    while True:
        try:
            user_input = read_input()
        except EOFError:
            print("\nBye")
            break
        except KeyboardInterrupt:
            print("\nAborted")
            break

        if user_input is None:
            print("Bye")
            break
        if not user_input.strip():
            continue
        if not user_input.endswith(";"):
            print("ERROR 1064 (42000): You have an error in your SQL syntax; check the manual that corresponds to your SBSQL server version for the right syntax to use near '' at end of line")
            continue

        user_input = user_input.strip()[:-1]

        if user_input.upper() == "HELP" or user_input.upper() == "\\H":
            print("""
For information about SBSQL commands, see:
https://sbsql.local/docs/

General statement syntax:
  SHOW TABLES;
  DESCRIBE <table_name>;
  SELECT <table_name>.<column_name> <row_index>;

Notes:
  - Statements must end with ';' or '\\g'.
  - Only read operations are supported in this edition.
  - For data modification, please contact your system administrator.
""")
            continue

        if user_input.upper() == "SHOW TABLES":
            tables = sbsql.scan_tables()
            if not tables:
                print("Empty set")
            else:
                print("+------------------+")
                print("| Tables_in_SBSQL  |")
                print("+------------------+")
                for t in tables:
                    print(f"| {t:<16} |")
                print("+------------------+")
            continue

        if user_input.upper().startswith("DESCRIBE "):
            try:
                parts = user_input.split()
                if len(parts) != 2:
                    print("ERROR 1064 (42000): You have an error in your SQL syntax")
                    continue
                table = parts[1]
                headers = sbsql.scan_headers(table)
                if isinstance(headers, dict) and headers.get("status") == "error":
                    print(headers['message'])
                    continue
                if not headers:
                    print("Empty set")
                else:
                    print(f"+-------+")
                    print(f"| Field |")
                    print(f"+-------+")
                    for h in headers:
                        print(f"| {h:<5} |")
                    print(f"+-------+")
            except (ValueError, TypeError) as e:
                print(e)
            continue

        if not user_input.upper().startswith("SELECT "):
            print("ERROR 1064 (42000): You have an error in your SQL syntax; check the manual that corresponds to your SBSQL server version for the right syntax to use near '%s'" % user_input.split()[0])
            continue

        parts = user_input.split()
        if len(parts) != 3:
            print("ERROR 1064 (42000): You have an error in your SQL syntax")
            continue

        table_dot_item = parts[1]
        index_str = parts[2]

        if "." in table_dot_item:
            table = table_dot_item.split(".")[0]
            item = table_dot_item.split(".")[1]
        else:
            print("ERROR 1064 (42000): Table and column must be separated by '.'")
            continue

        try:
            index = int(index_str)
            if index < 0:
                raise ValueError
        except (ValueError, TypeError):
            print("ERROR 1210 (HY000): Invalid argument for row index")
            continue

        try:
            result = sbsql.get(table, item, index)
            if result["status"] == "ok":
                print(f"+------+")
                print(f"| row {index:<3} |")
                print(f"+------+")
                print(f"| {result['data']:<4} |")
                print(f"+------+")
            else:
                print(f"ERROR: {result['message']}")
        except (ValueError, TypeError) as e:
            print(e)


if __name__ == "__main__":
    main()
