# testGrid — GRID API quick tests

Purpose: simple standalone scripts to verify that your GRID API key and a test series ID return JSON and to inspect the raw shape of responses.

Environment
- Set your API key and test series id in environment variables:

```bash
export GRID_API_KEY="your-grid-api-key-here"
export GRID_TEST_SERIES_ID="your-test-series-id-here"
```

Requirements
- Python 3.11+
- Install `httpx` in your environment:

```bash
python -m pip install --upgrade pip
python -m pip install httpx
```

Files
- `test_list_files.py`: Calls `GET https://api.grid.gg/file-download/list/{SERIES_ID}` and prints HTTP status, response headers, and pretty JSON body.
- `test_end_state.py`: Calls `GET https://api.grid.gg/file-download/end-state/grid/series/{SERIES_ID}`, prints HTTP status, top-level JSON keys, and a ~2000-character pretty-printed preview.

How to run

```bash
python test_list_files.py
python test_end_state.py
```

What success looks like
- HTTP 200 OK and pretty-printed JSON output in the console.

Common errors
- `401` — bad key (check `GRID_API_KEY`).
- `403` — key has no access to that series.
- `404` — the series has no files yet or the series ID is wrong.

Notes
- Scripts print raw responses and will exit non-zero on errors so failures are loud and obvious.
- These scripts intentionally avoid FastAPI, pandas, or other frameworks — they are tiny single-file checks.

Using a .env file
------------------

You can store the values needed for testing in a local `.env` file inside the `testGrid/` directory. A template is provided in `testGrid/.env.example`.

1. Copy the example to a real `.env` and edit it:

```bash
cp testGrid/.env.example testGrid/.env
# edit testGrid/.env and fill values
```

2. Load the variables into your shell (recommended so they are exported):

```bash
# POSIX shells (bash/zsh): export all variables from the file into the environment
set -a; source testGrid/.env; set +a

# or explicitly source if your .env contains `export VAR=...` lines:
source testGrid/.env
```

3. Run the scripts as before:

```bash
python3 testGrid/test_list_files.py
python3 testGrid/test_end_state.py
```

Security note: Keep `testGrid/.env` out of version control. If you use git, add `testGrid/.env` to your `.gitignore` file.

