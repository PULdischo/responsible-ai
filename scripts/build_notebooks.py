"""
Build script: clean Colab-specific metadata from notebooks,
export each to HTML (read-only preview), and copy the cleaned
.ipynb as the "run anywhere" variant.

Usage:
    python scripts/build_notebooks.py
"""

import copy
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
NOTEBOOKS_DIR = ROOT / "notebooks"
RUN_ANYWHERE_DIR = NOTEBOOKS_DIR / "run-anywhere"
HTML_DIR = ROOT / "assets" / "notebooks" / "html"
TMP_DIR = ROOT / ".tmp_notebooks"

# Google Colab-specific patterns to replace in source cells
COLAB_SUBSTITUTIONS = [
    # drive.mount
    (
        "from google.colab import drive",
        "# from google.colab import drive  # Colab only — replaced below",
    ),
    (
        "drive.mount('/content/drive')",
        (
            "# drive.mount('/content/drive')  # Colab only\n"
            "# Set this to your local data folder instead:\n"
            "import os\n"
            "drive_folder = os.environ.get('DATA_FOLDER', 'data/')"
        ),
    ),
    # files.upload
    (
        "from google.colab import files\nuploaded = files.upload()",
        (
            "# from google.colab import files  # Colab only — replaced below\n"
            "# Provide local file paths instead:\n"
            "from pathlib import Path\n"
            "uploaded = {p.name: p.read_bytes() for p in Path('data/').glob('*') if p.is_file()}"
        ),
    ),
    # userdata.get
    (
        "from google.colab import userdata",
        (
            "# from google.colab import userdata  # Colab only — replaced below\n"
            "import os\n"
            "# Load API keys from environment variables or a .env file:\n"
            "# pip install python-dotenv  then add your key to a .env file\n"
            "try:\n"
            "    from dotenv import load_dotenv\n"
            "    load_dotenv()\n"
            "except ImportError:\n"
            "    pass  # install python-dotenv if you use a .env file"
        ),
    ),
    (
        "userdata.get(",
        "os.environ.get(",
    ),
]

PREAMBLE_MARKDOWN = """\
> **Running outside Google Colab?**  
> This notebook has been adapted for use in any Jupyter environment (local Jupyter, VS Code, JupyterHub, etc.).  
> Colab-specific cells (file upload, Google Drive mount, secret manager) have been replaced with portable equivalents.  
> See the comments in each affected cell for instructions.
>
> To use your own data, place files in a `data/` folder next to this notebook, or set the `DATA_FOLDER`
> environment variable to the path of your data directory.  
> Store API keys in a `.env` file (requires `pip install python-dotenv`) or set them as environment variables.
"""


def clean_output_metadata(cell: dict) -> dict:
    """Remove Colab-specific fields from cell outputs so nbconvert doesn't choke."""
    cell = copy.deepcopy(cell)
    for output in cell.get("outputs", []):
        # Remove Colab-specific error detail field
        output.pop("errorDetails", None)
        # Remove problematic widget state
        if "application/vnd.jupyter.widget-view+json" in output.get("data", {}):
            output["data"].pop("application/vnd.jupyter.widget-view+json", None)
        if "application/vnd.google.colaboratory.intrinsic+json" in output.get("data", {}):
            output["data"].pop("application/vnd.google.colaboratory.intrinsic+json", None)
    return cell


def clean_notebook_metadata(nb: dict) -> dict:
    """Remove Colab-specific top-level metadata."""
    nb = copy.deepcopy(nb)
    nb.get("metadata", {}).pop("colab", None)
    nb.get("metadata", {}).pop("widgets", None)
    return nb


def apply_colab_substitutions(source: str) -> tuple[str, bool]:
    """Replace Colab-specific code patterns with portable equivalents."""
    changed = False
    for old, new in COLAB_SUBSTITUTIONS:
        if old in source:
            source = source.replace(old, new)
            changed = True
    return source, changed


def make_run_anywhere(nb: dict) -> dict:
    """Return a copy of the notebook with Colab cells made portable."""
    nb = copy.deepcopy(nb)

    preamble_inserted = False
    new_cells = []

    for cell in nb.get("cells", []):
        if cell.get("cell_type") == "code":
            source = "".join(cell.get("source", []))
            new_source, changed = apply_colab_substitutions(source)
            if changed:
                cell["source"] = [new_source]
                cell["outputs"] = []
                cell["execution_count"] = None
                if not preamble_inserted:
                    preamble_cell = {
                        "cell_type": "markdown",
                        "metadata": {},
                        "source": [PREAMBLE_MARKDOWN],
                    }
                    new_cells.append(preamble_cell)
                    preamble_inserted = True
        new_cells.append(cell)

    nb["cells"] = new_cells
    return nb


def write_cleaned_for_html(nb: dict, tmp_path: Path) -> None:
    """Write a version of the notebook with problematic output metadata stripped."""
    nb = copy.deepcopy(nb)
    nb = clean_notebook_metadata(nb)
    nb["cells"] = [clean_output_metadata(c) for c in nb.get("cells", [])]
    tmp_path.write_text(json.dumps(nb, ensure_ascii=False, indent=1))


def main():
    TMP_DIR.mkdir(exist_ok=True)
    HTML_DIR.mkdir(parents=True, exist_ok=True)
    RUN_ANYWHERE_DIR.mkdir(exist_ok=True)

    notebooks = sorted(NOTEBOOKS_DIR.glob("*.ipynb"))
    print(f"Found {len(notebooks)} notebooks")

    errors = []
    for nb_path in notebooks:
        print(f"\n→ {nb_path.name}")
        try:
            nb = json.loads(nb_path.read_text())
        except json.JSONDecodeError as e:
            print(f"  ✗ JSON parse error: {e}")
            errors.append(nb_path.name)
            continue

        # --- HTML preview (cleaned tmp copy) ---
        tmp_path = TMP_DIR / nb_path.name
        write_cleaned_for_html(nb, tmp_path)

        result = subprocess.run(
            [
                sys.executable, "-m", "nbconvert",
                "--to", "html",
                "--output-dir", str(HTML_DIR),
                str(tmp_path),
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print("  ✓ HTML exported")
        else:
            print(f"  ✗ HTML export failed:\n{result.stderr[-800:]}")
            errors.append(nb_path.name)

        # --- Run-anywhere .ipynb ---
        run_anywhere_nb = make_run_anywhere(nb)
        out_path = RUN_ANYWHERE_DIR / nb_path.name
        out_path.write_text(json.dumps(run_anywhere_nb, ensure_ascii=False, indent=1))
        print("  ✓ run-anywhere notebook written")

    # Clean up tmp dir
    shutil.rmtree(TMP_DIR, ignore_errors=True)

    if errors:
        print(f"\n⚠ Finished with errors in: {', '.join(errors)}")
        sys.exit(1)
    else:
        print(f"\n✓ All {len(notebooks)} notebooks processed successfully")


if __name__ == "__main__":
    main()
