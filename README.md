# ChildReach

## Identifying Child Vulnerability Hotspots in Mozambique Through Spatial Data Fusion

ChildReach is a graduate-level spatial data fusion project focused on Mozambique. The project will prototype an interactive decision-support tool that combines multiple public spatial datasets to help users explore where child vulnerability indicators overlap.

This project is being developed for the **AI Application Engineer for Spatial Learning Path**.

## Learning Path Goal

Prototype an interactive or intelligent tool that uses fused spatial data.

## Project Goal

Develop a simple working demo, likely in Jupyter first and later Streamlit, that helps students, planners, or humanitarian analysts understand district-level child vulnerability patterns in Mozambique.

The tool will use fused spatial datasets to show how combining administrative boundaries, gridded population estimates, and later vulnerability indicators can provide more useful context than any single dataset alone.

## Core Spatial Fusion Idea

ChildReach starts by combining at least two spatial data sources:

1. **Mozambique ADM2 administrative boundaries**
   - Source: geoBoundaries / Mozambique INE / OCHA ROSEA
   - Role: district-level analysis units

2. **WorldPop under-age-18 population raster**
   - Source: WorldPop
   - Role: estimated population under age 18 at approximately 100m resolution

The first fusion step summarizes raster population cells inside ADM2 district polygons using zonal statistics. This creates a district-level table and map of estimated children under 18.

Milestone 2 adds an IPC acute food insecurity layer. The newest available IPC snapshot was inspected first, but it covers only part of the country, so the broader November 2022 IPC period is used as the main report-safe vulnerability layer.

## Milestone 1: ADM2 + WorldPop Under-18 Population Fusion — Complete

The first completed milestone builds and validates a district-level map of Mozambique showing estimated population under age 18 for 2019.

This milestone includes:

- Inspecting and validating ADM2 boundary data
- Inspecting WorldPop raster metadata and values
- Confirming CRS and spatial overlap between vector and raster data
- Using zonal statistics to aggregate raster population estimates by district
- Handling NoData and missing raster-support cases transparently
- Producing an initial district-level choropleth map

Completed outputs:

- `data/processed/moz_adm2_under18_2019.gpkg` — spatial ADM2 dataset with joined WorldPop under-18 estimates
- `data/processed/moz_adm2_under18_2019.csv` — non-spatial table for inspection and reporting
- `figures/moz_adm2_under18_2019_choropleth.png` — first district-level under-18 population map

Two island ADM2 features, `Ilha Licom` and `Ilha Risunodo`, are retained with missing under-18 totals because they have no valid WorldPop raster cells in this product. These are treated as missing raster-support cases, not as zero population.

WorldPop filename interpretation for the raster used in Milestone 1:

- `moz` — Mozambique
- `T` — total population across both sexes
- `Under_18` — people under age 18
- `2019` — represented year
- `CN` — constrained estimate
- `100m` — 3 arc-second grid, approximately 100m at the equator
- `R2025A_v1` — WorldPop release/version

The WorldPop source describes these data as estimated people per grid square, not density, so district-level `sum` zonal statistics are appropriate. The processed ADM2 table sums to approximately `15,339,674.46` estimated under-18 people across the 157 districts with valid raster support. The full source raster sums to approximately `15,350,762.00`, so the ADM2 aggregation captures about `99.93%` of the raster total; the remaining difference is a small boundary/raster-support discrepancy to document rather than silently impute.

Citation for the under-age-18 raster product:

> Bondarenko M., Priyatikanto R., Tejedor-Garavito N., Zhang W., McKeen T., Cunningham A., Woods T., Hilton J., Cihan D., Nosatiuk B., Brinkhoff T., Tatem A., Sorichetta A. Estimates of total number of people under the age of 18 years old and broken down by male and female for each year 2015-2030 at a resolution of 3 arc (approximately 100m at the equator) R2025A version v1. Global Demographic Data Project - Funded by The Bill and Melinda Gates Foundation (INV-045237). WorldPop - School of Geography and Environmental Science, University of Southampton. DOI:10.5258/SOTON/WP00847

## Milestone 2: IPC Acute Food Insecurity Layer — Current Handoff

The second milestone inspects Mozambique IPC acute food insecurity data and prepares a district-level vulnerability layer for later maps and dashboard work.

The project first evaluates the latest IPC snapshot because it is the most current. That July 2026 layer covers 46 of 159 ADM2 records, representing about 24.72% of the 2019 under-18 population in the existing ADM2 + WorldPop baseline. Because this leaves most districts without IPC coverage, the latest layer is retained as methodological evidence but not used as the main national layer.

For broader spatial representation, the workflow then uses the HDX all-area IPC file and filters to the November 2022 current analysis period (`2022-10-01` to `2023-03-31`). That period contains 159 IPC area records. Diagnostic matching showed that IPC areas and geoBoundaries ADM2 names are not perfectly identical, so the notebook applies only conservative one-to-one name crosswalks for city and spelling variants. The safe join matches 145 of 159 ADM2 rows to IPC area records, and 137 rows have a non-missing `Phase 3+ percentage current` metric. Unmatched or non-comparable rows are retained as missing values rather than assumed to have zero food insecurity.

Milestone 2 outputs:

- `notebooks/10_inspect_ipc_food_insecurity.ipynb` — cleaned, executable notebook documenting the 2026 latest-data check, the 2022 broader-coverage decision, and the safe IPC-to-ADM2 join.
- `data/processed/moz_adm2_under18_ipc_current.csv` — July 2026 latest IPC comparison output, shape `(159, 16)`.
- `data/processed/moz_adm2_under18_ipc_2022_safe.csv` — November 2022 safe IPC join output, shape `(159, 18)`.
- `figures/moz_ipc_phase3plus_current_2026.png` — latest IPC comparison figure.

The IPC layer should be described as an area-level acute food insecurity indicator, not a child-specific food insecurity count. The exploratory exposure proxy multiplies district under-18 population by the IPC Phase 3+ fraction and should be interpreted as a prioritization/support indicator, not a precise estimate of food-insecure children.

## Reproducible Environment

Install the Python dependencies with:

```bash
python -m pip install -r requirements.txt
```

The notebook workflow currently depends on GeoPandas, Rasterio, rasterstats, Shapely, pandas, NumPy, Matplotlib, Requests, JupyterLab, and ipykernel. The project also imports the local `childreach` package from `src/`, so notebooks should be run from the repository root or with the repository's `src/` directory on `PYTHONPATH`.

## Next Milestone

Create final map outputs and a lightweight dashboard/demo from the validated ADM2 + WorldPop + IPC layers. The next working step should start with static map design before building dashboard interactivity.

## Planned Working Demo

The final demo should be a working Jupyter notebook, Streamlit app, or Google Colab that allows a user to:

- view district-level under-18 population estimates
- compare fused spatial indicators once additional datasets are added
- identify areas where multiple vulnerability indicators overlap
- understand the data sources, assumptions, and limitations behind the map

The demo is intended as a decision-support and learning tool, not an automated aid-allocation system.

## Project Structure

```text
child_reach_spacial_project/
├── app/                 # Future Streamlit or interactive app code
├── data/
│   ├── raw/             # Original downloaded data files
│   ├── interim/         # Intermediate analysis outputs
│   └── processed/       # Reproducible final analysis-ready outputs
├── figures/             # Generated maps and visual outputs
├── notebooks/           # Exploratory analysis and learning notebooks
├── report/              # Paper, presentation, and writing assets
├── src/
│   ├── analysis/        # Analysis scripts
│   ├── data/            # Data loading/acquisition scripts
│   ├── features/        # Feature engineering scripts
│   └── spatial/         # Spatial processing utilities
└── README.md
```

## Ethical Framing

This project supports further humanitarian assessment; it does not determine aid allocation or identify individual children.

All results should be interpreted as aggregate, model-based estimates that depend on the selected data sources, boundary definitions, raster resolution, and spatial aggregation methods.
