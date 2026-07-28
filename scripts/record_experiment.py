"""
Automated Experiment & Test Results Recorder.

Generates a standardized Markdown report under docs/benchmarks/EXP-XXX.md
and appends an entry into docs/EXPERIMENTS.md.
"""

from datetime import datetime, timezone
import argparse
import os
import subprocess
import sys


def get_git_commit_hash() -> str:
    """Returns short commit hash of current git workspace."""
    try:
        res = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return res.stdout.strip()
    except Exception:
        return "uncommitted"


def main():
    parser = argparse.ArgumentParser(description="Record an experiment run in docs/EXPERIMENTS.md")
    parser.add_argument("--title", type=str, required=True, help="Short title of the experiment")
    parser.add_argument("--script", type=str, required=True, help="Script path used for testing")
    parser.add_argument("--summary", type=str, default="", help="Brief summary of findings")
    args = parser.parse_args()

    docs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs"))
    benchmarks_dir = os.path.join(docs_dir, "benchmarks")
    os.makedirs(benchmarks_dir, exist_ok=True)

    experiments_md = os.path.join(docs_dir, "EXPERIMENTS.md")

    # Determine next experiment ID
    existing_files = [f for f in os.listdir(benchmarks_dir) if f.endswith(".md")]
    exp_num = len(existing_files) + 1
    exp_id = f"EXP-{exp_num:03d}"
    filename = f"{exp_num:03d}_{args.title.lower().replace(' ', '_')}.md"
    file_path = os.path.join(benchmarks_dir, filename)

    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    commit_hash = get_git_commit_hash()

    # Generate Report Template
    report_content = f"""# {exp_id}: {args.title}

- **Fecha de Ejecución:** {now_str}
- **Versión del Código / Commit:** `{commit_hash}`
- **Script Utilizado:** `{args.script}`
- **Objetivo:** {args.summary or 'Ejecución y registro de prueba.'}

---

## ⚙️ Configuración y Parámetros

- **Entorno:** Python {sys.version.split()[0]}
- **Modo:** Live / Benchmark

---

## 📊 Resultados Obtenidos

| Métrica | Valor |
|---|---|
| ... | ... |

---

## 💡 Conclusiones

- Reporte autogenerado el {now_str}.
"""

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    print(f"✅ Created experiment report: {file_path}")

    # Append to EXPERIMENTS.md if it exists
    if os.path.exists(experiments_md):
        entry_row = f"| **{exp_id}** | {now_str[:16]} | `{commit_hash}` | {args.title} | ✅ Completado | [{filename}](benchmarks/{filename}) |\n"
        with open(experiments_md, "a", encoding="utf-8") as f:
            f.write(entry_row)
        print(f"✅ Appended entry to {experiments_md}")


if __name__ == "__main__":
    main()
