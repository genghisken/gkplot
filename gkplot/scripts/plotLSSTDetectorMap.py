"""
189 labeled squares arranged as:
- Row 1 (bottom): 3 groups
- Row 2: 5 groups, centered over Row 1
- Row 3: 5 groups, centered over Row 2
- Row 4: 5 groups, centered over Row 3
- Row 5 (top): 3 groups aligned with the *middle three* of Row 4

Each group is a 3×3 of unit squares labeled:
6 7 8
3 4 5
0 1 2

Numbering proceeds by groups left→right in each row, bottom→top:
0–8, 9–17, 18–26, ..., up to 188.

Color any sets of labels by editing `labels_by_color` below.
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch
from matplotlib.colors import to_rgb


def draw_grid(
    labels_by_color=None,
    square_size=1.0,
    intra_gap=0.12,
    inter_gap_x=0.6,
    inter_gap_y=0.6,
    label_fs=7.5,
    fill_alpha=0.85,
    show_legend=True,
    save_path=None,
):
    """Draw and label the 189 squares; color those listed in `labels_by_color`.

    Args:
        labels_by_color (dict[str, list[int]]): e.g. {"problem":[58,98], "missing":[34,28]}
        square_size (float): side length of each small square.
        intra_gap (float): gap inside a 3×3 group between neighboring squares.
        inter_gap_x (float): horizontal gap between groups.
        inter_gap_y (float): vertical gap between rows.
        label_fs (float): font size for numeric labels.
        fill_alpha (float): alpha for colored squares.
        show_legend (bool): include a legend for the colored sets.
        save_path (str|None): if given, save the figure to this path.

    Returns:
        (fig, ax)
    """
    if labels_by_color is None:
        labels_by_color = {}

    # Allow a friendly "problem" name; pass through other named/hex colors
    friendly_map = {"problem": "#FFBF00", "missing": "#FF0000"}

    def resolve_color(name_or_hex: str) -> str:
        return friendly_map.get(str(name_or_hex).lower(), name_or_hex)

    def label_contrast(fill_color: str) -> str:
        """Pick black/white label based on fill luminance for readability."""
        try:
            r, g, b = to_rgb(fill_color)
            L = 0.2126 * r + 0.7152 * g + 0.0722 * b
            return "black" if L > 0.6 else "white"
        except Exception:
            return "black"

    # Build quick lookup: label -> (facecolor, textcolor)
    color_lookup = {}
    for cname, labels in labels_by_color.items():
        fc = resolve_color(cname)
        tc = label_contrast(fc)
        for lab in labels:
            color_lookup[lab] = (fc, tc)  # later entries win on conflicts

    # --- Geometry for groups and rows ---
    group_w = 3 * square_size + 2 * intra_gap
    group_h = 3 * square_size + 2 * intra_gap
    stride_x = group_w + inter_gap_x
    stride_y = group_h + inter_gap_y

    # Row pattern bottom→top
    row_groups = [3, 5, 5, 5, 3]

    # X positions for group centers
    row_x_positions = []

    # Row 0: 3 groups centered at x=0
    k = row_groups[0]
    row0 = [(i - (k - 1) / 2) * stride_x for i in range(k)]
    row_x_positions.append(row0)

    # Rows 1–3: five groups centered over the previous row's *center*
    for r in [1, 2, 3]:
        k = row_groups[r]  # 5
        prev_center = sum(row_x_positions[r - 1]) / len(row_x_positions[r - 1])
        xs = [prev_center + (i - (k - 1) / 2) * stride_x for i in range(k)]
        row_x_positions.append(xs)

    # Row 4: three groups aligned with the middle three of row 3
    row4 = [row_x_positions[3][1], row_x_positions[3][2], row_x_positions[3][3]]
    row_x_positions.append(row4)

    # Y positions for rows
    row_y_positions = [r * stride_y for r in range(len(row_groups))]

    # --- Draw ---
    fig, ax = plt.subplots(figsize=(9, 11))
    group_idx = 0
    total_squares = 0

    for y_center, xs in zip(row_y_positions, row_x_positions):
        for x_center in xs:
            base = 9 * group_idx  # 0, 9, 18, ...
            group_idx += 1

            gx0 = x_center - group_w / 2
            gy0 = y_center - group_h / 2

            for iy in range(3):      # 0 (bottom) .. 2 (top)
                for ix in range(3):  # 0 (left) .. 2 (right)
                    x = gx0 + ix * (square_size + intra_gap)
                    y = gy0 + iy * (square_size + intra_gap)
                    label = base + iy * 3 + ix  # -> 0..8 in the required pattern

                    # Fill color and contrasting text color
                    fc = None
                    tc = "black"
                    if label in color_lookup:
                        fc, tc = color_lookup[label]

                    rect = Rectangle(
                        (x, y),
                        square_size,
                        square_size,
                        linewidth=1.0,
                        edgecolor="black",
                        facecolor=fc if fc else "none",
                        alpha=fill_alpha if fc else 1.0,
                    )
                    ax.add_patch(rect)
                    ax.text(
                        x + square_size / 2,
                        y + square_size / 2,
                        str(label),
                        ha="center",
                        va="center",
                        fontsize=label_fs,
                        color=tc,
                    )
                    total_squares += 1

    # Legend for selected sets
    if show_legend and labels_by_color:
        patches = [
            Patch(facecolor=resolve_color(c), edgecolor="black", alpha=fill_alpha, label=c)
            for c in labels_by_color.keys()
        ]
        ax.legend(handles=patches, title="Detectors", loc="upper right")

    # Tidy up axes
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")
    pad = square_size
    xmin = min(min(xs) for xs in row_x_positions) - (group_w / 2 + pad)
    xmax = max(max(xs) for xs in row_x_positions) + (group_w / 2 + pad)
    ymin = -(group_h / 2 + pad)
    ymax = row_y_positions[-1] + group_h / 2 + pad
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)

    if save_path:
        fig.savefig(save_path, dpi=200, bbox_inches="tight")

    print(f"Total squares drawn: {total_squares} (labels 0..188)")
    return fig, ax


if __name__ == "__main__":
    # Example usage — edit these lists freely:
    labels_by_color = {
        "problem": [22, 117, 163, 178, 186],
        "missing":   [0, 1, 19, 20, 27, 30, 65, 68, 120, 122, 123, 158, 161, 168, 169, 187, 188],
        # Add more sets/colors if you like:
        # "blue": [12, 13, 42],
        # "#7f00ff": [5, 6, 7],
    }

    fig, ax = draw_grid(
        labels_by_color=labels_by_color,
        save_path="squares_colored.png",  # set to None to skip saving
    )
    plt.show()

