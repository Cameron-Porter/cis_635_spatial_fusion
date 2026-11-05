"""Render report maps from saved 2019 ADM2 geometry and safe 2022 IPC metrics.

Run from the repository root with PYTHONPATH=src python -m childreach.final_maps.
No downloads or notebook execution are required.
"""

from pathlib import Path

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.patches import Patch
import numpy as np
import pandas as pd

from childreach.paths import (
    DATA_PROCESSED, FIGURES_DIR, MOZ_ADM2_UNDER18_2019_GPKG,
    MOZ_ADM2_UNDER18_2019_LAYER,
)

IPC_CSV = DATA_PROCESSED / "moz_adm2_under18_ipc_2022_safe.csv"
PERCENT = "phase3plus_percent_current"
FRACTION = "phase3plus_fraction_current"
PROXY = "under18_phase3plus_exposure_proxy_2022"
FROM, TO = "2022-10-01", "2023-03-31"


def join_2022_metrics(districts: gpd.GeoDataFrame, ipc: pd.DataFrame) -> gpd.GeoDataFrame:
    """Join exactly one CSV record per saved district; reject inconsistent metrics."""
    for label, frame in (("districts", districts), ("IPC CSV", ipc)):
        if frame.shapeID.isna().any():
            raise ValueError(f"{label} contains null shapeID")
        if frame.shapeID.duplicated().any():
            raise ValueError(f"{label} contains duplicate shapeID")
    if set(districts.shapeID) != set(ipc.shapeID):
        raise ValueError("shapeID sets differ between GPKG and IPC CSV")

    joined = districts.merge(
        ipc[["shapeID", PERCENT, FRACTION, PROXY, "current_from", "current_to"]],
        on="shapeID", how="left", validate="one_to_one", sort=False,
    )
    pct = pd.to_numeric(joined[PERCENT], errors="raise")
    fraction = pd.to_numeric(joined[FRACTION], errors="raise")
    proxy = pd.to_numeric(joined[PROXY], errors="raise")
    population = pd.to_numeric(joined["under18_sum"], errors="raise")
    if not pct.notna().equals(fraction.notna()) or not np.allclose(
        pct.dropna(), fraction.dropna() * 100, rtol=0, atol=1e-6
    ) or ((pct.dropna() < 0) | (pct.dropna() > 100)).any():
        raise ValueError("IPC percentage and fraction disagree or are outside 0–100%")
    expected = population * fraction
    if not proxy.notna().equals(expected.notna()) or not np.allclose(
        proxy.dropna(), expected.dropna(), rtol=1e-6, atol=1e-4
    ):
        raise ValueError("under-18 exposure proxy disagrees with 2019 under-18 × 2022 IPC fraction")
    dated = joined[PERCENT].notna()
    if not ((joined.loc[dated, "current_from"] == FROM) &
            (joined.loc[dated, "current_to"] == TO)).all():
        raise ValueError("IPC metrics must refer to the Oct 2022–Mar 2023 current period")
    return joined


def render_maps(joined: gpd.GeoDataFrame, output_dir: Path) -> tuple[Path, Path]:
    """Save distinct percent and under-18 exposure-proxy maps with missing hatching."""
    specs = (
        (PERCENT, "IPC Phase 3+ share · Mozambique ADM2", "IPC Phase 3+ share of analyzed population (%)",
         "moz_ipc_phase3plus_percent_2022.png", "YlOrRd", 50,
         "Area-level IPC acute food insecurity; not child-specific."),
        (PROXY, "Under-18 Phase 3+ exposure proxy · Mozambique ADM2", "Under-18 exposure proxy (estimated people)",
         "moz_under18_phase3plus_exposure_proxy_2022.png", "PuRd", 65000,
         "Proxy = 2019 estimated under-18 population × 2022 IPC Phase 3+ fraction.\n"
         "Not a measured count of food-insecure children."),
    )
    output_dir = Path(output_dir)
    outputs = []
    for column, title, scale_label, filename, palette, vmax, caveat in specs:
        fig, ax = plt.subplots(figsize=(10, 10))
        fig.subplots_adjust(left=0.06, right=0.88, top=0.89, bottom=0.15)
        known = joined[column].notna()
        joined.loc[known].plot(column=column, ax=ax, cmap=palette,
                               vmin=0, vmax=vmax, edgecolor="#454545", linewidth=0.22)
        if (~known).any():
            joined.loc[~known].plot(ax=ax, color="#d8d8d8", hatch="///",
                                    edgecolor="#555555", linewidth=0.3)
        sm = plt.cm.ScalarMappable(norm=Normalize(0, vmax), cmap=palette)
        colorbar = fig.colorbar(sm, ax=ax, fraction=0.04, pad=0.02)
        colorbar.set_label(scale_label)
        ax.legend(handles=[Patch(facecolor="#d8d8d8", edgecolor="#555555",
                                 hatch="///", label=f"Missing / not comparable ({(~known).sum()} districts)")],
                  loc="lower left", frameon=True, fontsize=9)
        ax.set_title(title, fontsize=14, weight="bold", pad=14)
        ax.set_axis_off()
        fig.text(0.06, 0.055,
                 "IPC analysis: Nov 2022; current period: 1 Oct 2022–31 Mar 2023.\n"
                 + caveat + "\nSources: geoBoundaries ADM2; WorldPop under-18 (2019); IPC safe join (2022).",
                 fontsize=8.5, va="bottom", linespacing=1.45)
        output = output_dir / filename
        fig.savefig(output, dpi=200, facecolor="white")
        plt.close(fig)
        outputs.append(output)
    return tuple(outputs)


def main() -> None:
    districts = gpd.read_file(MOZ_ADM2_UNDER18_2019_GPKG, layer=MOZ_ADM2_UNDER18_2019_LAYER)
    ipc = pd.read_csv(IPC_CSV, dtype={"shapeID": str})
    joined = join_2022_metrics(districts, ipc)
    for path, column in zip(render_maps(joined, FIGURES_DIR), (PERCENT, PROXY)):
        print(f"{path}: {joined[column].notna().sum()} mapped districts")


if __name__ == "__main__":
    main()
