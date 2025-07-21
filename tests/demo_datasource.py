import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Any, Optional
import sqlite3


class SQLiteDataSourceMixin:
    def __init__(self, page_size=10):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.page_size = page_size
        self._table = "records"
        self._where = ""
        self._order_by = ""
        self._page = 0
        self._columns = []

    @classmethod
    def _infer_type(cls, value: Any) -> str:
        if isinstance(value, int):
            return "INTEGER"
        elif isinstance(value, float):
            return "REAL"
        elif isinstance(value, bytes):
            return "BLOB"
        return "TEXT"

    def set_data(self, records: List[Dict[str, Any]]):
        if not records:
            return

        self._columns = list(records[0].keys())
        col_types = {col: self._infer_type(records[0][col]) for col in self._columns}
        col_definitions = ", ".join(f"{col} {col_types[col]}" for col in self._columns)

        self.conn.execute(f"DROP TABLE IF EXISTS {self._table}")
        self.conn.execute(f"CREATE TABLE {self._table} ({col_definitions})")

        with self.conn:
            for row in records:
                placeholders = ", ".join("?" for _ in self._columns)
                values = tuple(row.get(col) for col in self._columns)
                self.conn.execute(f"INSERT INTO {self._table} VALUES ({placeholders})", values)

    def set_filter(self, where_sql: str = ""):
        self._where = where_sql

    def set_sort(self, order_by_sql: str = ""):
        self._order_by = order_by_sql

    def get_page(self, page: Optional[int] = None) -> List[Dict[str, Any]]:
        if page is not None:
            self._page = page
        offset = self._page * self.page_size

        query = f"SELECT * FROM {self._table}"
        if self._where:
            query += f" WHERE {self._where}"
        if self._order_by:
            query += f" ORDER BY {self._order_by}"
        query += f" LIMIT {self.page_size} OFFSET {offset}"

        cursor = self.conn.execute(query)
        return [dict(row) for row in cursor.fetchall()]

    def next_page(self):
        self._page += 1
        return self.get_page()

    def prev_page(self):
        self._page = max(0, self._page - 1)
        return self.get_page()

    def total_count(self) -> int:
        query = f"SELECT COUNT(*) FROM {self._table}"
        if self._where:
            query += f" WHERE {self._where}"
        return self.conn.execute(query).fetchone()[0]
