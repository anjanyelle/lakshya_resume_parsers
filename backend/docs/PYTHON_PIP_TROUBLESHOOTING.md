# Python & pip Troubleshooting (ModuleNotFoundError)

**Problem:** Package installed in one Python, script running in another → `ModuleNotFoundError` even after installation.

---

## STEP 1 — Check which Python is running

```bash
where python
where pip
```

If they point to **different locations** → that’s the problem.

---

## STEP 2 — Check if the package is actually installed

Example for spaCy:

```bash
pip show spacy
```

- If installed → you see version + location.
- If nothing prints → not installed (or installed for a different Python).

---

## STEP 3 — Safe install (use same interpreter)

**Always use:**

```bash
python -m pip install spacy
```

**Avoid:**

```bash
pip install spacy
```

`python -m pip` installs into the **same** Python that runs your script.

---

## STEP 4 — Upgrade if already installed

```bash
python -m pip install --upgrade spacy
```

---

## STEP 5 — Check inside Python

```bash
python
```

Then:

```python
import spacy
print(spacy.__version__)
```

- No error → installed correctly.
- Error → wrong environment.

Exit with `exit()`.

---

## STEP 6 — SpaCy model (not just the package)

Error example:

```text
OSError: Can't find model 'en_core_web_sm'
```

Fix:

```bash
python -m spacy download en_core_web_sm
```

Test:

```python
import spacy
nlp = spacy.load("en_core_web_sm")
print("Model loaded successfully")
```

---

## Common cause: multiple Pythons

You may have:

- Python 3.11
- Python 3.12
- Anaconda
- VS Code using a different interpreter

**In VS Code:**

1. `Ctrl+Shift+P`
2. Type: **Python: Select Interpreter**
3. Pick the same Python you use in the terminal for `python -m pip`.

---

## Master debug (run first)

```bash
python -m pip --version
python --version
```

If the paths/versions don’t match what you expect → environment issue.

---

## Clean reinstall

```bash
python -m pip uninstall spacy
python -m pip install spacy --no-cache-dir
python -m spacy download en_core_web_sm
```

---

## Permission error (Windows)

- Run CMD/PowerShell as Administrator, or
- Install for your user only:

```bash
python -m pip install spacy --user
```

---

## Auto check + install (project script)

To check and install using the **current** interpreter:

```python
import importlib
import subprocess
import sys

package = "spacy"

try:
    importlib.import_module(package)
    print(f"{package} is already installed")
except ImportError:
    print(f"{package} not installed. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
```

This uses `sys.executable`, so the install goes to the same Python that runs the script.

---

## Quick summary

| Do this                         | Avoid this           |
| ------------------------------- | -------------------- |
| `python -m pip install package` | `pip install ...`    |
| `python -m spacy download ...`  | `spacy download ...` |

When not using a virtual environment, always use the interpreter explicitly: `python -m pip` and `python -m spacy`.
