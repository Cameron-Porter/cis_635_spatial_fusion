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

Later project phases may add additional vulnerability indicators such as malnutrition, poverty, food insecurity, health access, or other humanitarian datasets. Those additions should be documented carefully before being incorporated into the final index or dashboard.

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

## Next Milestone

Select and document a second vulnerability-relevant spatial dataset, then decide how it should be harmonized to the ADM2 analysis units before adding it to the fused dataset.

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
