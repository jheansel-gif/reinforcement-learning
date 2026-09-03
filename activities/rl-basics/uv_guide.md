# UV Setup Guide (Windows / PowerShell)

## I. Install UV (Run Once)

Open **PowerShell** and run:

```powershell
powershell -ExecutionPolicy Bypass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Add UV to PATH (if not automatically added)

Replace `{your_user}` with your Windows username:

```powershell
[Environment]::SetEnvironmentVariable(
  "Path",
  $env:Path + ";C:\Users\{your_user}\.local\bin",
  [EnvironmentVariableTarget]::User
)
```

Restart PowerShell.

Verify installation:

```powershell
uv --version
```

---

## II. Python Itself

You do **not** need to install Python separately. UV downloads and manages
interpreters for you.

`pyproject.toml` declares the required version:

```toml
requires-python = ">=3.12,<3.14"
```

`uv venv` and `uv sync` read that constraint and fetch a matching interpreter
automatically if one is not already available. No python.org installer, no
PATH juggling, no `py` launcher.

Useful commands:

```powershell
uv python list          # show available and installed interpreters
uv python install 3.12  # pre-install a specific version
uv venv --python 3.12   # pin this project's environment to a version
```

Interpreters are cached per user, so several projects can pin different
Python versions without conflicting.

---

## III. Project Setup (Per Project)

Navigate to your project directory:

```powershell
cd path\to\your\project
```

Create the environment and install everything from `pyproject.toml` +
`uv.lock`:

```powershell
uv sync
```

`uv sync` creates `.venv` on its own — a separate `uv venv` is only needed
when you want the environment before installing anything, or want to pin a
specific interpreter.

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

### Editable Mode

For a project with a `[build-system]` (like this one), `uv sync` installs the
project itself in **editable** mode.

A normal install *copies* your package into `.venv\Lib\site-packages`. The
copy is what gets imported, so every source edit requires reinstalling before
Python sees it.

An editable install copies nothing. It writes a small link into
`site-packages` pointing back at your working tree, so `import` loads the
real files under `src/`. Edit a source file and the next interpreter run
picks the change up immediately — no reinstall.

This is what you want while developing a package. Reinstall only when
*packaging metadata* changes (dependencies, entry points, the package
layout), not when code changes.

---

## IV. Daily Workflow

Activate the environment:

```powershell
.venv\Scripts\Activate.ps1
```

Sync dependencies (after pulling changes, or when the lockfile moved):

```powershell
uv sync
```

Run Python:

```powershell
python main.py
```

Or skip activation entirely — `uv run` resolves the environment itself and
syncs it first if it is stale:

```powershell
uv run python main.py
uv run jupyter lab
```

### Notebooks: Editable Install Is Not Enough

An editable install means a *fresh* interpreter sees your latest source. A
Jupyter kernel is not fresh — it caches every module in `sys.modules` on
first import; re-running the import cell is a no-op against that cache.
Edits to `src/` will not appear until you restart the kernel.

To pick up source changes without restarting, put this in the first cell,
*before* the imports:

```python
%load_ext autoreload
%autoreload 2
```

`%autoreload 2` re-imports changed modules before every cell execution.

It has limits. Existing instances keep working because their class methods
get patched in place, but these still need a kernel restart:

- new or removed *attributes* on an existing object
- changes to a class's base classes, decorators, dataclasses, or enums
- anything bound by `from module import name` at import time, since the old
  object stays in your namespace

When behaviour stops matching the source, restart the kernel before
debugging further.

---

## V. Managing Dependencies

### Add Dependency

```powershell
uv add package-name
```

This updates `pyproject.toml` and `uv.lock`, and installs into `.venv`.
Commit both files.

### Remove Dependency

```powershell
uv remove package-name
```

### Re-resolve the Lockfile

After editing `pyproject.toml` by hand:

```powershell
uv lock       # re-resolve to match pyproject.toml
uv sync       # apply the result to .venv
```

Upgrade a single pinned package:

```powershell
uv lock --upgrade-package package-name
```

---

## VI. Rebuild Environment (Clean Reset)

```powershell
deactivate
Remove-Item -Recurse -Force .venv
uv sync
```

---

## VII. Rules

- Commit `pyproject.toml` and `uv.lock`.
- Never commit `.venv/`.
- Use `uv add` / `uv remove`, not `pip install`.
- Edit `pyproject.toml` by hand only if you follow with `uv lock`.
- Let UV supply the interpreter; do not hand-install Python.

Deterministic environments require lockfile discipline.
