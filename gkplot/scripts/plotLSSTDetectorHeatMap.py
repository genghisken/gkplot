import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.patches import Patch
from matplotlib.colors import Normalize, to_rgb
import matplotlib.cm as cm
from gkutils.commonutils import readGenericDataFile

# ---------- Helpers ----------

def parse_detector_table(raw: str) -> dict[int, float]:
    """
    Parse a 2-column table like:
        | detector | number |
        |      2   |  2014  |
    Returns: {detector_label: value, ...}
    Lines not starting with '|' or without two ints are ignored.
    """
    out = {}
    for line in raw.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        toks = [t.strip() for t in line.strip("|").split("|")]
        if len(toks) >= 2 and toks[0].isdigit() and toks[1].isdigit():
            out[int(toks[0])] = float(toks[1])
    return out

def _contrast_for(facecolor):
    try:
        r, g, b = to_rgb(facecolor)
        L = 0.2126*r + 0.7152*g + 0.0722*b
        return "black" if L > 0.6 else "white"
    except Exception:
        return "black"

# Friendly names for colormaps (use whatever names you prefer)
FRIENDLY_CMAP = {
    "warm": "inferno",
    "cool": "viridis",
    "fire": "magma",
    "ocean": "cividis",
    "gray": "Greys",
    "rainbow": "turbo",
    "amber": "YlOrBr",
}
def resolve_cmap(name: str):
    return FRIENDLY_CMAP.get(str(name).lower(), name)

# ---------- Main drawing routine (heatmap) ----------

def draw_grid_heatmap(
    values: dict[int, float],
    *,
    square_size=1.0,
    intra_gap=0.12,
    inter_gap_x=0.6,
    inter_gap_y=0.6,
    label_fs=7.0,
    cmap="viridis",          # can be a Matplotlib cmap name OR a friendly name above
    vmin=None,
    vmax=None,
    show_colorbar=True,
    show_detector_ids=True,  # label each square with its detector number (0..188)
    annotate_values=False,   # put the numeric value instead (or alongside)
    missing_color="#eeeeee", # detectors with no value get this fill
    save_path=None,
):
    """
    Render the 189 detectors as a heatmap using your 3×3 group layout.
    `values` maps detector_id -> detection count.
    """
    # --- geometry identical to your previous version ---
    group_w = 3 * square_size + 2 * intra_gap
    group_h = 3 * square_size + 2 * intra_gap
    stride_x = group_w + inter_gap_x
    stride_y = group_h + inter_gap_y
    row_groups = [3, 5, 5, 5, 3]

    row_x_positions = []
    k = row_groups[0]
    row0 = [(i - (k - 1)/2) * stride_x for i in range(k)]
    row_x_positions.append(row0)

    for r in [1, 2, 3]:
        k = row_groups[r]
        prev_center = sum(row_x_positions[r-1]) / len(row_x_positions[r-1])
        xs = [prev_center + (i - (k - 1)/2) * stride_x for i in range(k)]
        row_x_positions.append(xs)

    row4 = [row_x_positions[3][1], row_x_positions[3][2], row_x_positions[3][3]]
    row_x_positions.append(row4)

    row_y_positions = [r * stride_y for r in range(len(row_groups))]

    # --- heatmap setup ---
    cmap = cm.get_cmap(resolve_cmap(cmap))
    present_vals = list(values.values()) if values else []
    if vmin is None: vmin = min(present_vals) if present_vals else 0.0
    if vmax is None: vmax = max(present_vals) if present_vals else 1.0
    norm = Normalize(vmin=vmin, vmax=vmax, clip=True)

    fig, ax = plt.subplots(figsize=(9, 11))
    group_idx = 0
    total = 0

    for y_center, xs in zip(row_y_positions, row_x_positions):
        for x_center in xs:
            base = 9 * group_idx
            group_idx += 1

            gx0 = x_center - group_w/2
            gy0 = y_center - group_h/2

            for iy in range(3):
                for ix in range(3):
                    det_id = base + iy*3 + ix  # 0..188 with your pattern

                    x = gx0 + ix*(square_size + intra_gap)
                    y = gy0 + iy*(square_size + intra_gap)

                    if det_id in values:
                        face = cmap(norm(values[det_id]))
                    else:
                        face = missing_color

                    rect = Rectangle((x, y), square_size, square_size,
                                     edgecolor="black", facecolor=face, linewidth=1.0)
                    ax.add_patch(rect)

                    # choose label text
                    txt = None
                    if annotate_values and show_detector_ids:
                        txt = f"{det_id}\n{int(values[det_id]) if det_id in values else '–'}"
                    elif annotate_values:
                        txt = f"{int(values[det_id])}" if det_id in values else "–"
                    elif show_detector_ids:
                        txt = f"{det_id}"

                    if txt is not None:
                        ax.text(x + square_size/2, y + square_size/2, txt,
                                ha="center", va="center", fontsize=label_fs,
                                color=_contrast_for(face))

                    total += 1

    # Frame and colorbar
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")

    if show_colorbar and present_vals:
        sm = cm.ScalarMappable(norm=norm, cmap=cmap)
        cbar = fig.colorbar(sm, ax=ax, fraction=0.030, pad=0.02)
        cbar.set_label("Detections")

    # margins
    pad = square_size
    xmin = min(min(xs) for xs in row_x_positions) - (group_w/2 + pad)
    xmax = max(max(xs) for xs in row_x_positions) + (group_w/2 + pad)
    ymin = - (group_h/2 + pad)
    ymax = row_y_positions[-1] + group_h/2 + pad
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)

    if save_path:
        fig.savefig(save_path, dpi=200, bbox_inches="tight")

    print(f"Drawn {total} squares (0..188). vmin={vmin}, vmax={vmax}")
    return fig, ax

# ---------- Example usage ----------
if __name__ == "__main__":
    # Paste your two-column table here (detector | number)
    raw_table = """
    |        2 |   2014 |
    |        3 |   2114 |
    |        4 |   1969 |
    |        5 |   2247 |
    |        6 |   2166 |
    |        7 |   2941 |
    |        8 |   3017 |
    |        9 |   1879 |
    |       10 |   1978 |
    |       11 |   1831 |
    |       12 |   2364 |
    |       13 |   2363 |
    |       14 |   2286 |
    |       15 |   2572 |
    |       16 |   2874 |
    |       17 |   2663 |
    |       18 |   1988 |
    |       21 |   2236 |
    |       22 |   2049 |
    |       23 |   2128 |
    |       24 |   2686 |
    |       25 |   2405 |
    |       26 |   2208 |
    |       28 |   2183 |
    |       29 |   2218 |
    |       31 |   2212 |
    |       32 |   2584 |
    |       33 |   2092 |
    |       34 |   2285 |
    |       35 |   2692 |
    |       36 |   2653 |
    |       37 |   3004 |
    |       38 |   3111 |
    |       39 |   2895 |
    |       40 |   3006 |
    |       41 |   3202 |
    |       42 |   2892 |
    |       43 |   3157 |
    |       44 |   3355 |
    |       45 |   3205 |
    |       46 |   2966 |
    |       47 |   3060 |
    |       48 |   3303 |
    |       49 |   3267 |
    |       50 |   3016 |
    |       51 |   3314 |
    |       52 |   3394 |
    |       53 |   3266 |
    |       54 |   2820 |
    |       55 |   2810 |
    |       56 |   2555 |
    |       57 |   2999 |
    |       58 |   3262 |
    |       59 |   2758 |
    |       60 |   3023 |
    |       61 |   2956 |
    |       62 |   2943 |
    |       63 |   2362 |
    |       64 |   2165 |
    |       66 |   2791 |
    |       67 |   2363 |
    |       69 |   2777 |
    |       70 |   2361 |
    |       71 |   1968 |
    |       72 |   1782 |
    |       73 |   2435 |
    |       74 |   2710 |
    |       75 |   1879 |
    |       76 |   2473 |
    |       77 |   2458 |
    |       78 |   1870 |
    |       79 |   2212 |
    |       80 |   2698 |
    |       81 |   2992 |
    |       82 |   3047 |
    |       83 |   3553 |
    |       84 |   3136 |
    |       85 |   2999 |
    |       86 |   3226 |
    |       87 |   2976 |
    |       88 |   3024 |
    |       89 |   3045 |
    |       90 |   3320 |
    |       91 |   3363 |
    |       92 |   3354 |
    |       93 |   3270 |
    |       94 |   3719 |
    |       95 |   3508 |
    |       96 |   3382 |
    |       97 |   3825 |
    |       98 |   3491 |
    |       99 |   3007 |
    |      100 |   2907 |
    |      101 |   3010 |
    |      102 |   3232 |
    |      103 |   3153 |
    |      104 |   2786 |
    |      105 |   3640 |
    |      106 |   3229 |
    |      107 |   3037 |
    |      108 |   2817 |
    |      109 |   2160 |
    |      110 |   2065 |
    |      111 |   2889 |
    |      112 |   2400 |
    |      113 |   1962 |
    |      114 |   2751 |
    |      115 |   2153 |
    |      116 |   1900 |
    |      117 |   2004 |
    |      118 |   2374 |
    |      119 |   3046 |
    |      121 |   2367 |
    |      124 |   2292 |
    |      125 |   2460 |
    |      126 |   2974 |
    |      127 |   3115 |
    |      128 |   3212 |
    |      129 |   2939 |
    |      130 |   3122 |
    |      131 |   3304 |
    |      132 |   2869 |
    |      133 |   3095 |
    |      134 |   3076 |
    |      135 |   3349 |
    |      136 |   3210 |
    |      137 |   3126 |
    |      138 |   3102 |
    |      139 |   3057 |
    |      140 |   3141 |
    |      141 |   3052 |
    |      142 |   2965 |
    |      143 |   2945 |
    |      144 |   3282 |
    |      145 |   3278 |
    |      146 |   2954 |
    |      147 |   3017 |
    |      148 |   3015 |
    |      149 |   2764 |
    |      150 |   2859 |
    |      151 |   2941 |
    |      152 |   2725 |
    |      153 |   2904 |
    |      154 |   2236 |
    |      155 |   1863 |
    |      156 |   2588 |
    |      157 |   2226 |
    |      159 |   2515 |
    |      160 |   2037 |
    |      162 |   2325 |
    |      163 |   3100 |
    |      164 |   2550 |
    |      165 |   2059 |
    |      166 |   2130 |
    |      167 |   2157 |
    |      170 |   1921 |
    |      171 |   2756 |
    |      172 |   2438 |
    |      173 |   3051 |
    |      174 |   2398 |
    |      175 |   2202 |
    |      176 |   2417 |
    |      177 |   2051 |
    |      178 |   2023 |
    |      179 |   1910 |
    |      180 |   2343 |
    |      181 |   2398 |
    |      182 |   2538 |
    |      183 |   2250 |
    |      184 |   2103 |
    |      185 |   1947 |
    |      186 |   1861 |
    """

#    data = readGenericDataFile("/Users/kws/lasair/lsst/run_20251009/heatmap_all_detections.csv", delimiter=',')
#    data = readGenericDataFile("/Users/kws/lasair/lsst/run_20251009/heatmap_all_detections_minus_diaobjectid0.csv", delimiter=',')
#    data = readGenericDataFile("/Users/kws/lasair/lsst/run_20251009/heatmap_all_detections_minus_singletons_and_diaobjectid0.csv", delimiter=',')
#    data = readGenericDataFile("/Users/kws/lasair/lsst/run_20251009/heatmap_all_detections_minus_singletons_and_diaobjectid0_reliability_gt_99.csv", delimiter=',')
    data = readGenericDataFile("/Users/kws/lasair/lsst/run_20251009/heatmap_all_detections_minus_diaobjectid0_reliability_gt_99.csv", delimiter=',')

    values = {}
    for row in data:
        values[int(row['detector'])] = float(row['ndet'])


    #values = parse_detector_table(raw_table)


    # Choose a colormap by friendly name or direct name, e.g. "warm" or "inferno"
    fig, ax = draw_grid_heatmap(
        values,
        cmap="warm",            # friendly -> "inferno"
        annotate_values=False,  # set True to print the numbers inside
        show_detector_ids=True, # show detector ids (0..188)
        save_path="detector_heatmap.png",
    )
#    plt.title("All Detections (463,396)")
#    plt.title("All Detections minus diaObjectId = 0 (419,462)")
#    plt.title("All Detections minus diaObjectId = 0 and minus all singletons (62,424)")
#    plt.title("All Detections minus diaObjectId = 0 and minus all singletons and reliability > 0.99 (2,709)")
    plt.title("All Detections minus diaObjectId = 0 and reliability > 0.99 (35,240)")
    plt.tight_layout()
    plt.show()

