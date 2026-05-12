from __future__ import annotations

import uuid
from pathlib import Path

import matplotlib.pyplot as plt


def run_matplotlib(code: str, filename: str | None = None) -> str:
    """Execute matplotlib code that uses 'plt' and 'ax', then save the figure.

    Available global variables are limited to the following (sandboxing):
    enumerate, range, list, len, min, max, sum, dict, plt, fig, ax, zip

    Args:
        code (str): Python code that assumes 'plt' and 'ax' are already defined.
        filename (str | None): Desired filename (e.g. 'sales_by_region.png').
            If omitted, a random name is used.

    Returns:
        str: Absolute path to the saved PNG file.

    """
    fig, ax = plt.subplots()

    safe_builtins = {
        "enumerate": enumerate,
        "range": range,
        "list": list,
        "len": len,
        "min": min,
        "max": max,
        "sum": sum,
        "dict": dict,
        "zip": zip,
    }

    safe_globals = {
        "__builtins__": safe_builtins,
        "plt": plt,
        "fig": fig,
        "ax": ax,
    }

    compiled = compile(code, "<visualizer_code>", "exec")
    exec(compiled, safe_globals)  # noqa: S102

    if not filename:
        filename = f"plot_{uuid.uuid4().hex}.png"
    if not filename.endswith(".png"):
        filename += ".png"

    filepath = Path(filename).resolve()
    fig.savefig(filepath, bbox_inches="tight")
    plt.close(fig)
    return str(filepath)
