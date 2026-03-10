"""Generate matplotlib charts as 300 DPI PNGs from a ChartRequest JSON file."""

import argparse
import json
import sys
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
from pydantic import ValidationError

matplotlib.use("Agg")

# Allow imports from the scripts package
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.models import ChartRequest

DEFAULT_COLORS = [
    "#1B3A5C",
    "#4A7FB5",
    "#7BAFD4",
    "#A8D5E2",
    "#6B7B8D",
    "#9EAAB6",
    "#C4CDD5",
    "#E8ECEF",
]
TITLE_COLOR = "#1B3A5C"


def format_dollar(value: float) -> str:
    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:.1f}M"
    elif abs(value) >= 1_000:
        return f"${value / 1_000:.0f}k"
    else:
        return f"${value:.0f}"


def _colors(style_colors: list[str] | None) -> list[str]:
    return style_colors if style_colors else DEFAULT_COLORS


def _setup_axes(ax: plt.Axes, title: str) -> None:
    ax.set_title(title, color=TITLE_COLOR, fontsize=14, fontweight="bold")
    ax.grid(False)
    ax.set_axisbelow(False)


def draw_horizontal_bar(chart, ax: plt.Axes) -> None:
    labels = chart.data.labels
    values = chart.data.values[0]
    colors = _colors(chart.style.colors)

    bars = ax.barh(labels, values, color=[colors[i % len(colors)] for i in range(len(labels))])
    for bar, v in zip(bars, values):
        ax.text(
            bar.get_width(),
            bar.get_y() + bar.get_height() / 2,
            f" {format_dollar(v)}",
            va="center",
            fontsize=9,
        )
    ax.invert_yaxis()
    _setup_axes(ax, chart.title)


def draw_grouped_bar(chart, ax: plt.Axes) -> None:
    import numpy as np

    labels = chart.data.labels
    series = chart.data.values
    series_names = chart.data.series_names or [f"Series {i}" for i in range(len(series))]
    colors = _colors(chart.style.colors)

    n_groups = len(labels)
    n_series = len(series)
    bar_width = 0.8 / n_series
    x = np.arange(n_groups)

    for idx, (row, name) in enumerate(zip(series, series_names)):
        offset = x + idx * bar_width - (n_series - 1) * bar_width / 2
        bars = ax.bar(offset, row, bar_width, label=name, color=colors[idx % len(colors)])
        for bar, v in zip(bars, row):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height(),
                format_dollar(v),
                ha="center",
                va="bottom",
                fontsize=8,
            )

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
    _setup_axes(ax, chart.title)


def draw_waterfall(chart, ax: plt.Axes) -> None:
    labels = list(chart.data.labels)
    increments = list(chart.data.values[0])
    colors = _colors(chart.style.colors)

    cumulative = []
    running = 0.0
    for inc in increments:
        cumulative.append(running)
        running += inc

    # Append total bar
    labels.append("Total")
    total = running
    increments.append(total)
    cumulative.append(0)

    bar_colors = []
    for i in range(len(increments) - 1):
        bar_colors.append(colors[i % len(colors)])
    bar_colors.append(colors[0])  # total bar uses first color

    bars = ax.bar(labels, increments, bottom=cumulative, color=bar_colors)
    for bar, inc, bot in zip(bars, increments, cumulative):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bot + inc,
            format_dollar(inc if bar != bars[-1] else total),
            ha="center",
            va="bottom",
            fontsize=8,
        )

    _setup_axes(ax, chart.title)


def draw_error_bar(chart, ax: plt.Axes) -> None:
    labels = chart.data.labels
    midpoints = chart.data.values[0]
    error_low = chart.data.error_low or [0] * len(midpoints)
    error_high = chart.data.error_high or [0] * len(midpoints)
    colors = _colors(chart.style.colors)

    yerr_lower = [m - lo for m, lo in zip(midpoints, error_low)]
    yerr_upper = [hi - m for m, hi in zip(midpoints, error_high)]

    bars = ax.bar(
        labels,
        midpoints,
        color=[colors[i % len(colors)] for i in range(len(labels))],
        yerr=[yerr_lower, yerr_upper],
        capsize=5,
        ecolor="#333333",
    )
    for bar, v in zip(bars, midpoints):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            format_dollar(v),
            ha="center",
            va="bottom",
            fontsize=8,
        )

    _setup_axes(ax, chart.title)


RENDERERS = {
    "horizontal_bar": draw_horizontal_bar,
    "grouped_bar": draw_grouped_bar,
    "waterfall": draw_waterfall,
    "error_bar": draw_error_bar,
}


def generate_charts(request: ChartRequest, output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    generated: list[Path] = []

    plt.rcParams["font.family"] = "sans-serif"

    for chart in request.charts:
        fig, ax = plt.subplots(figsize=chart.style.figsize)
        renderer = RENDERERS.get(chart.chart_type.value)
        if renderer is None:
            print(f"Unknown chart type: {chart.chart_type}", file=sys.stderr)
            plt.close(fig)
            continue
        renderer(chart, ax)
        fig.tight_layout()

        out_path = output_dir / f"{chart.chart_id}.png"
        fig.savefig(str(out_path), dpi=chart.style.dpi, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        generated.append(out_path)

    return generated


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate charts from a ChartRequest JSON file.")
    parser.add_argument("--input", required=True, help="Path to ChartRequest JSON file")
    parser.add_argument("--output-dir", required=True, help="Directory to write PNGs")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(input_path) as f:
            raw = json.load(f)
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        request = ChartRequest(**raw)
    except ValidationError as exc:
        print(f"Validation error: {exc}", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args.output_dir)
    generated = generate_charts(request, output_dir)

    for p in generated:
        print(p)


if __name__ == "__main__":
    main()
