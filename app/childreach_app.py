"""ChildReach saved-data demo. Run: PYTHONPATH=src streamlit run app/childreach_app.py"""

from pathlib import Path
import sys

# Streamlit runs this file as a script, outside the package's src directory.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import pandas as pd

from childreach.final_maps import IPC_CSV, PERCENT, PROXY, join_2022_metrics
from childreach.paths import MOZ_ADM2_UNDER18_2019_GPKG, MOZ_ADM2_UNDER18_2019_LAYER

POPULATION = "under18_sum"
METRICS = {
    POPULATION: ("2019 estimated under-18 population", "Blues"),
    PERCENT: ("2022 IPC Phase 3+ share of analyzed population (%)", "YlOrRd"),
    PROXY: ("2019 under-18 × 2022 IPC Phase 3+ exposure proxy", "PuRd"),
}


def load_data(gpkg=MOZ_ADM2_UNDER18_2019_GPKG, csv=IPC_CSV):
    """Read saved layers and validate the shapeID join and period/metric invariants."""
    districts = gpd.read_file(gpkg, layer=MOZ_ADM2_UNDER18_2019_LAYER)
    ipc = pd.read_csv(csv, dtype={"shapeID": str})
    return join_2022_metrics(districts, ipc)


def coverage(data, metric):
    """Return (available, missing, total); zero is available, not missing."""
    available = int(data[metric].notna().sum())
    return available, len(data) - available, len(data)


def top_proxy(data, n):
    """Rank only districts with a comparable exposure proxy."""
    return (data.loc[data[PROXY].notna(), ["shapeID", "shapeName", PROXY]]
            .sort_values([PROXY, "shapeID"], ascending=[False, True])
            .head(n).reset_index(drop=True))


def district_options(data):
    """Use shapeID as the unambiguous selector value even for duplicate names."""
    return dict(zip(data.shapeID, data.shapeName + " · " + data.shapeID))


def draw_map(data, metric, selected_id=None):
    """Plot one indicator; hatch unavailable districts rather than showing zero."""
    fig, ax = plt.subplots(figsize=(9, 8))
    known = data[metric].notna()
    if known.any():
        data.loc[known].plot(column=metric, ax=ax, cmap=METRICS[metric][1],
                             legend=True, edgecolor="#555555", linewidth=0.2,
                             legend_kwds={"label": METRICS[metric][0]})
    if (~known).any():
        data.loc[~known].plot(ax=ax, color="#d8d8d8", hatch="///",
                              edgecolor="#555555", linewidth=0.3)
        ax.legend(handles=[Patch(facecolor="#d8d8d8", edgecolor="#555555",
                                 hatch="///", label="Missing / not comparable")],
                  loc="lower left")
    if selected_id is not None:
        data.loc[data.shapeID == selected_id].boundary.plot(ax=ax, color="#087e83",
                                                             linewidth=2.2)
    ax.set_axis_off()
    ax.set_title(METRICS[metric][0])
    fig.tight_layout()
    return fig


def main():
    import streamlit as st

    st.set_page_config(page_title="ChildReach Mozambique", layout="wide")
    st.title("ChildReach · Mozambique districts")
    st.caption("ADM2 learning and decision-support demo · 2019 WorldPop baseline + November 2022 IPC analysis")
    try:
        data = load_data()
    except (OSError, ValueError, KeyError) as exc:
        st.error(f"Cannot load validated saved data: {exc}")
        st.stop()

    metric = st.sidebar.selectbox("Map indicator", list(METRICS),
                                  format_func=lambda value: METRICS[value][0])
    options = district_options(data)
    selected_id = st.sidebar.selectbox("Find district (type to search)",
                                        [None, *options],
                                        format_func=lambda value: options[value] if value else "All districts")
    available, missing, total = coverage(data, metric)
    st.info(f"Coverage for this indicator: {available} of {total} districts available; "
            f"{missing} missing / not comparable (hatched, not zero).")
    map_col, details_col = st.columns([2, 1])
    with map_col:
        fig = draw_map(data, metric, selected_id)
        st.pyplot(fig)
        plt.close(fig)
    with details_col:
        if selected_id:
            row = data.loc[data.shapeID == selected_id].iloc[0]
            st.subheader(f"{row.shapeName} · {selected_id}")
            for column, (label, _) in METRICS.items():
                value = row[column]
                displayed = "Missing / not comparable" if pd.isna(value) else (
                    f"{value:,.1f}%" if column == PERCENT else f"{value:,.0f}")
                st.write(f"**{label}:** {displayed}")
        st.subheader("Highest exposure proxies")
        n = st.slider("Top N comparable districts", 5, 30, 10)
        st.dataframe(top_proxy(data, n).rename(columns={PROXY: "Exposure proxy (estimated)"}),
                     hide_index=True)
        st.caption("Ranked proxy, not a count of measured food-insecure children or a needs priority score.")

    st.markdown("""### Sources and limits
- **Geography:** geoBoundaries Mozambique ADM2 district polygons (`shapeID` join).
- **Population:** WorldPop estimated under-18 population, **2019**. This is not a 2022 child census.
- **Food insecurity:** IPC Phase 3+ share of the **analyzed population**, November **2022** analysis; current period **1 Oct 2022–31 Mar 2023**. It is not child-specific.
- **Exposure proxy:** 2019 under-18 estimate × 2022 IPC area-level Phase 3+ fraction. The years differ; this is **not a measured count of food-insecure children**. Missing or non-comparable IPC joins remain missing, not zero. No 2026 snapshot is mixed into this view.
- District-level patterns are exploratory; do not use this display alone to allocate aid.
""")


if __name__ == "__main__":
    main()
