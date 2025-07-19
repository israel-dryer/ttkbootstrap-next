import sqlite3
from typing import Any, Dict, List, Optional


class DataSourceMixin:
    """Provides in-memory SQLite-backed data management with pagination,
    sorting, filtering, and inferred schema support.

    This mixin is intended to be used with UI components such as
    paginated lists or tables that require efficient access to large
    datasets without re-rendering the full list.
    """

    def __init__(self, page_size: int = 10):
        """Initializes the SQLite data source.

        Args:
            page_size: The number of records per page for pagination.
        """
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
        """Infers the SQLite column type based on a Python value.

        Args:
            value: A sample value from the dataset.

        Returns:
            A string representing the SQLite-compatible type ('INTEGER', 'REAL', 'TEXT', or 'BLOB').
        """
        if isinstance(value, int):
            return "INTEGER"
        elif isinstance(value, float):
            return "REAL"
        elif isinstance(value, bytes):
            return "BLOB"
        return "TEXT"

    def set_data(self, records: List[Dict[str, Any]]):
        """Loads records into the SQLite database and creates a schema based on inferred types.

        Args:
            records: A list of dictionaries, each representing a data row.
        """
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
        """Sets the WHERE clause used to filter data results.

        Args:
            where_sql: SQL WHERE clause (excluding the 'WHERE' keyword).
        """
        self._where = where_sql

    def set_sort(self, order_by_sql: str = ""):
        """Sets the ORDER BY clause used to sort data results.

        Args:
            order_by_sql: SQL ORDER BY clause (excluding the 'ORDER BY' keyword).
        """
        self._order_by = order_by_sql

    def get_page(self, page: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieves a specific page of records based on the current filter and sort.

        Args:
            page: The page index to retrieve. If None, use the current page.

        Returns:
            A list of dictionaries representing rows for the selected page.
        """
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

    def next_page(self) -> List[Dict[str, Any]]:
        """Advances to the next page and returns the results.

        Returns:
            A list of dictionaries representing the next page of results.
        """
        self._page += 1
        return self.get_page()

    def prev_page(self) -> List[Dict[str, Any]]:
        """Goes back to the previous page and returns the results.

        Returns:
            A list of dictionaries representing the previous page of results.
        """
        self._page = max(0, self._page - 1)
        return self.get_page()

    def total_count(self) -> int:
        """Gets the total number of filtered records.

        Returns:
            The total count of rows matching the current filter.
        """
        query = f"SELECT COUNT(*) FROM {self._table}"
        if self._where:
            query += f" WHERE {self._where}"
        return self.conn.execute(query).fetchone()[0]
