from pathlib import Path

import nbformat as nbf


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "outputs" / "CO1_CO2_Solved_Notes.md"
OUTPUT = ROOT / "outputs" / "CO1_CO2_Solved_Notes.ipynb"


def split_markdown_into_cells(text: str) -> list[str]:
    cells: list[str] = []
    current: list[str] = []

    for line in text.splitlines():
        starts_new_section = (
            line.startswith("## ")
            or line.startswith("### ")
            or line.startswith("**Question:**")
        )
        if starts_new_section and current:
            cells.append("\n".join(current).strip() + "\n")
            current = []
        current.append(line)

    if current:
        cells.append("\n".join(current).strip() + "\n")

    return [cell for cell in cells if cell.strip()]


def main() -> None:
    markdown = SOURCE.read_text(encoding="utf-8")

    nb = nbf.v4.new_notebook()
    nb["metadata"] = {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {
            "name": "python",
            "pygments_lexer": "ipython3",
        },
    }

    nb.cells = [
        nbf.v4.new_markdown_cell(
            "# CO1 and CO2 Solved Notebook\n\n"
            "This notebook contains solved answers, diagrams, flowcharts, case studies, "
            "and worked numericals from the source question PDF.\n"
        )
    ]

    for cell_text in split_markdown_into_cells(markdown):
        if cell_text.startswith("# CO1 and CO2 Solved Notes"):
            continue
        nb.cells.append(nbf.v4.new_markdown_cell(cell_text))

    nb.cells.append(
        nbf.v4.new_code_cell(
            "# Numerical formula reference\n"
            "def latency(receive_ms, transmit_ms):\n"
            "    return receive_ms - transmit_ms\n\n"
            "def jitter(latencies_ms):\n"
            "    return max(latencies_ms) - min(latencies_ms)\n\n"
            "def average_latency(latencies_ms):\n"
            "    return sum(latencies_ms) / len(latencies_ms)\n\n"
            "def throughput(bits, seconds):\n"
            "    return bits / seconds\n\n"
            "def task_timing(release, start, completion, deadline):\n"
            "    return {\n"
            "        'waiting_time_ms': start - release,\n"
            "        'execution_time_ms': completion - start,\n"
            "        'response_time_ms': completion - release,\n"
            "        'deadline_margin_ms': deadline - completion,\n"
            "    }\n\n"
            "print('Latency example:', round(latency(17.9, 12.4), 1), 'ms')\n"
            "print('Jitter example:', jitter([4, 5, 7, 6]), 'ms')\n"
            "print('Throughput example:', throughput(32000, 0.020) / 1_000_000, 'Mbps')\n"
            "print('Task timing example:', task_timing(2, 5, 11, 15))\n"
        )
    )

    nbf.write(nb, OUTPUT)
    print(f"Wrote {OUTPUT}")
    print(f"Cells: {len(nb.cells)}")


if __name__ == "__main__":
    main()
