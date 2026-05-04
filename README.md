# module

Personal Oracle DB and analysis utilities. Copy-once, use everywhere.

---

## One-time setup

### 1. Install the package
```bash
pip install -e "C:/path/to/this/folder"
```
The `-e` flag means "editable" — any changes you make to the files are reflected immediately, no reinstall needed.

### 2. Set credentials via environment variables
Create a `.env` file in **each project** that uses this module:

```
ORACLE_USERNAME=your_username
ORACLE_PASSWORD=your_password
ORACLE_HOSTNAME=your_host
ORACLE_PORT=1521
ORACLE_SERVICE=your_service_name
```

Then load it at the top of your notebook or script:
```python
from dotenv import load_dotenv
load_dotenv()  # reads .env from current directory
```
Install dotenv once: `pip install python-dotenv`

---

## Usage

```python
# Option A — flat import (short)
from module import oracle_import, oracle_export, month_range

# Option B — explicit import (clear where it comes from)
from module.db.oracle import oracle_import, oracle_export
from module.utils.dates import month_range
```

### Common patterns

```python
# Query
df = oracle_import("SELECT * FROM my_table WHERE rownum <= 100")

# Export
oracle_export(df, "my_output_table", if_exists="replace")

# Load SQL from file
query = sql_open("src/query/my_query.sql")
df = oracle_import(query)

# Get last-day dates for past N months
dates = month_range(6)
# → ['20250228', '20250131', '20241231', '20241130', '20241031', '20240930']

# Use in query formatting
query = query.format(
    base_month=dates[0][:6],   # '202502'
    prev_month=dates[1][:6],   # '202501'
)
```

---

## Structure

```
module/
├── db/
│   └── oracle.py        # oracle_import, oracle_export, oracle_execute, sql_open
└── utils/
    ├── dates.py         # month_date_select, month_range
    └── misc.py          # drop_tmp_tables, set_float_format
```

Add new functions to the relevant file. If something grows large, give it its own file.
