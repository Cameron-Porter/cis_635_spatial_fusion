# Experiment Log

## 2026-09-18
Started ChildReach mentoring workflow. First milestone: district-level Mozambique map of estimated under-18 population.

Boundary validation results: 159 rows, CRS `EPSG:4326`, 0 missing geometries, 0 invalid geometries, 159 unique `shapeID` values, 0 duplicate `shapeID` values, 0 missing `shapeName` values, 159 unique `shapeName` values, all rows `shapeType=ADM2`, all rows `shapeGroup=MOZ`.

Created boundary preview figure at `figures/moz_adm2_boundaries_preview.png` for visual sanity-checking of the Mozambique ADM2 layer.

WorldPop candidate source identified at `https://hub.worldpop.org/geodata/listing?id=143`. The listing did not expose enough per-file metadata before download, so the next step is to place the downloaded raster/data package under `data/raw/` and inspect metadata locally before analysis.

First ADM2 zonal-statistics test with WorldPop total under-18 2019 raster completed using `stats=["sum", "count"]` and `nodata=-99999`. Output shape was `(159, 2)`, matching the 159 ADM2 features. `count` had 0 missing values; `sum` had 2 missing values that need inspection before saving processed results.

Inspected the two ADM2 features with missing WorldPop under-18 sums. `Ilha Licom` (`85939544B53859921366962`) and `Ilha Risunodo` (`85939544B49635827229265`) both had `valid_cell_count = 0` and `under18_sum = NaN`. This indicates no valid, non-NoData WorldPop cells contributed to those polygons under the default zonal-statistics method; the missing sums are not a join failure.

Compared default zonal-statistics behavior with `all_touched=True` for the two missing island features. Both `Ilha Licom` and `Ilha Risunodo` remained `count = 0` and `sum = NaN` under `all_touched=True`. This suggests the missing values are not merely caused by the default cell-center rule missing tiny polygons; the WorldPop raster provides no valid cells for these features in this product.

Created an in-memory joined results GeoDataFrame with `under18_sum`, `valid_cell_count`, and `worldpop_valid_cells = valid_cell_count > 0`. Validation summary: 157 ADM2 features have valid WorldPop raster cells and 2 do not. For the 157 valid features, `under18_sum` ranged from about 1,746.81 to 473,215.63, with mean about 97,704.93 and median about 78,038.89. No negative under-18 sums were observed in the summary.

Sanity-checked largest and smallest ADM2 under-18 estimates. Highest values were major cities or populous districts, including `Cidade Da Matola` (~473,215.63), `Cidade De Maputo` (~442,010.88), `Cidade De Nampula` (~425,966.88), `Milange` (~363,712.44), and `Cidade Da Beira` (~291,995.78). Lowest valid values were sparse/small districts including `Lago Niassa` (~1,746.81), `Ibo` (~5,953.36), `Chigubo` (~10,106.42), `Massangena` (~11,658.72), and `Mecula` (~12,019.12). This supports the interpretation that the zonal results are broadly plausible before saving processed outputs.

Saved processed ADM2 + WorldPop under-18 outputs: spatial GeoPackage at `data/processed/moz_adm2_under18_2019.gpkg` and non-spatial CSV at `data/processed/moz_adm2_under18_2019.csv`. File existence and sizes were verified from the notebook: GeoPackage `9,134,080` bytes, CSV `10,967` bytes.

Read the processed outputs back from disk to verify reproducibility. The GeoPackage loaded with shape `(159, 9)` and CRS `EPSG:4326`; the CSV loaded with shape `(159, 8)`. The saved `worldpop_valid_cells` flag persisted correctly with 157 valid ADM2 features and 2 without valid WorldPop raster support.

Created and saved the first ADM2 under-18 choropleth map at `figures/moz_adm2_under18_2019_choropleth.png`. File existence and size were verified from the notebook: `521,910` bytes. This completes the first end-to-end map artifact from the fused ADM2 boundary + WorldPop raster workflow.

Milestone 1 closeout checks completed. Added `requirements.txt` from the working virtual environment so the notebook workflow can be recreated with pinned versions of GeoPandas, Rasterio, rasterstats, Shapely, pandas, NumPy, Matplotlib, Requests, JupyterLab, and ipykernel. Clarified `.gitignore` so notebook checkpoint directories are ignored as `notebooks/.ipynb_checkpoints/`.