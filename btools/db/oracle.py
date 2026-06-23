"""
Oracle DB helpers.
Credentials are loaded from environment variables.
Set these in a .env file at the project root (see README).
"""

import math
import os

import pandas as pd
from sqlalchemy import create_engine, types
from sqlalchemy.sql import text


# ---------------------------------------------------------------------------
# Connection — engines are module-level singletons (connection pool reuse)
# ---------------------------------------------------------------------------

def _build_connection_string() -> str:
    user     = os.environ["ORACLE_USERNAME"]
    password = os.environ["ORACLE_PASSWORD"]
    host     = os.environ["ORACLE_HOSTNAME"]
    port     = os.environ["ORACLE_PORT"]
    service  = os.environ["ORACLE_SERVICE"]
    return f"oracle+cx_oracle://{user}:{password}@{host}:{port}/?service_name={service}"


def _build_cms_connection_string() -> str:
    user     = os.environ["CMS_USERNAME"]
    password = os.environ["CMS_PASSWORD"]
    host     = os.environ["CMS_HOSTNAME"]
    port     = os.environ["CMS_PORT"]
    service  = os.environ["CMS_SERVICE"]
    return f"oracle+cx_oracle://{user}:{password}@{host}:{port}/?service_name={service}"


_engine_instance = None
_cms_engine_instance = None


def _engine():
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = create_engine(
            _build_connection_string(),
            pool_pre_ping=True
        )
    return _engine_instance


def _cms_engine():
    global _cms_engine_instance
    if _cms_engine_instance is None:
        _cms_engine_instance = create_engine(_build_cms_connection_string())
    return _cms_engine_instance


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _col_length(str_len) -> int:
    if not str_len or math.isnan(float(str_len)) or str_len < 1:
        return 64
    pw = int(math.log(str_len, 2))
    return int(math.ceil((str_len + 2 ** (pw - 1)) / 2 ** (pw - 1)) * 2 ** (pw - 1))


def _sql_col(data_frame: pd.DataFrame) -> dict:
    """Map pandas dtypes to SQLAlchemy column types."""
    dtypes_dict = {}
    for column, dtype in zip(data_frame.columns, data_frame.dtypes):
        dtype_str = str(dtype)
        if "object" in dtype_str or "str" in dtype_str:
            max_len = data_frame[column].str.len().max()
            dtypes_dict[column] = types.VARCHAR(length=_col_length(max_len))
        elif "datetime" in dtype_str:
            dtypes_dict[column] = types.DateTime()
        elif "float" in dtype_str:
            dtypes_dict[column] = types.FLOAT
        elif "int" in dtype_str:
            dtypes_dict[column] = types.INT()
    return dtypes_dict


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def cms_import(query: str) -> pd.DataFrame:
    """Run a SELECT query against CMS and return a DataFrame."""
    return pd.read_sql(query, _cms_engine())


def cms_export(
    data_frame: pd.DataFrame,
    table_name: str,
    index: bool = False,
    if_exists: str = "replace",
) -> None:
    """Export a DataFrame to a CMS Oracle table."""
    with _cms_engine().connect() as conn:
        data_frame.to_sql(
            table_name.lower(),
            con=conn,
            if_exists=if_exists,
            index=index,
            dtype=_sql_col(data_frame),
        )


def cms_execute(query: str) -> None:
    """Execute a non-SELECT statement on CMS. Auto-commits."""
    with _cms_engine().begin() as conn:
        conn.execute(text(query))


def oracle_import(query: str, params=None, chunksize: int = 100_000) -> pd.DataFrame:
    """Run a SELECT query and return a DataFrame.

    Reads in chunks to avoid MemoryError on large result sets.
    params: bind variables passed safely to the driver (prevents SQL injection).
    """
    chunks = list(pd.read_sql(query, _engine(), params=params, chunksize=chunksize))
    if not chunks:
        return pd.DataFrame()
    return pd.concat(chunks, ignore_index=True)


def oracle_export(
    data_frame: pd.DataFrame,
    table_name: str,
    index: bool = False,
    if_exists: str = "replace",
) -> None:
    """Export a DataFrame to an Oracle table."""
    with _engine().connect() as conn:
        data_frame.to_sql(
            table_name.lower(),
            con=conn,
            if_exists=if_exists,
            index=index,
            dtype=_sql_col(data_frame),
        )


def oracle_execute(query: str) -> None:
    """Execute a non-SELECT statement (DDL / DML). Auto-commits."""
    with _engine().begin() as conn:
        conn.execute(text(query))


def sql_open(filepath: str) -> str:
    """Read a .sql file and return its contents as a string.
    Tip: do not include a trailing semicolon in the file.
    """
    with open(os.path.normpath(filepath), mode="r", encoding="utf-8") as f:
        return f.read()
