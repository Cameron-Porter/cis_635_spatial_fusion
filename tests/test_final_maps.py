"""Invariants for the saved-data final map workflow (stdlib unittest)."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import geopandas as gpd
import pandas as pd
from shapely.geometry import box

from childreach.final_maps import join_2022_metrics, render_maps


def inputs():
    districts = gpd.GeoDataFrame(
        {"shapeID": ["a", "b", "c"], "under18_sum": [100.0, 200.0, None]},
        geometry=[box(i, 0, i + 1, 1) for i in range(3)], crs="EPSG:4326",
    )
    ipc = pd.DataFrame({
        "shapeID": ["c", "a", "b"],
        "phase3plus_percent_current": [None, 25.0, 0.0],
        "phase3plus_fraction_current": [None, 0.25, 0.0],
        "under18_phase3plus_exposure_proxy_2022": [None, 25.0, 0.0],
        "phase3plus_number_current": [None, 9999.0, 0.0],
        "current_from": [None, "2022-10-01", "2022-10-01"],
        "current_to": [None, "2023-03-31", "2023-03-31"],
    })
    return districts, ipc


class FinalMapTests(unittest.TestCase):
    def test_join_preserves_geometry_and_shapeid_order(self):
        districts, ipc = inputs()
        joined = join_2022_metrics(districts, ipc)
        self.assertEqual(joined.shapeID.tolist(), ["a", "b", "c"])
        self.assertTrue(joined.geometry.equals(districts.geometry))
        self.assertEqual(joined.phase3plus_percent_current.tolist()[:2], [25.0, 0.0])
        self.assertTrue(pd.isna(joined.phase3plus_percent_current.iloc[2]))

    def test_join_rejects_duplicate_shapeids(self):
        districts, ipc = inputs()
        districts.loc[1, "shapeID"] = "a"
        with self.assertRaisesRegex(ValueError, "duplicate shapeID"):
            join_2022_metrics(districts, ipc)
        districts, ipc = inputs()
        ipc.loc[1, "shapeID"] = "c"
        with self.assertRaisesRegex(ValueError, "duplicate shapeID"):
            join_2022_metrics(districts, ipc)

    def test_join_rejects_missing_or_unmatched_shapeids(self):
        districts, ipc = inputs()
        ipc.loc[0, "shapeID"] = "other"
        with self.assertRaisesRegex(ValueError, "shapeID sets differ"):
            join_2022_metrics(districts, ipc)
        ipc.loc[0, "shapeID"] = None
        with self.assertRaisesRegex(ValueError, "null shapeID"):
            join_2022_metrics(districts, ipc)

    def test_join_rejects_confusing_percent_fraction_or_proxy_with_ipc_count(self):
        districts, ipc = inputs()
        ipc.loc[1, "phase3plus_percent_current"] = 0.25
        with self.assertRaisesRegex(ValueError, "percentage and fraction disagree"):
            join_2022_metrics(districts, ipc)
        ipc.loc[1, "phase3plus_percent_current"] = 25.0
        ipc.loc[1, "under18_phase3plus_exposure_proxy_2022"] = 9999.0
        with self.assertRaisesRegex(ValueError, "exposure proxy disagrees"):
            join_2022_metrics(districts, ipc)

    def test_join_keeps_missing_metrics_missing_not_zero(self):
        districts, ipc = inputs()
        ipc.loc[2, "phase3plus_percent_current"] = None
        ipc.loc[2, "phase3plus_fraction_current"] = None
        ipc.loc[2, "under18_phase3plus_exposure_proxy_2022"] = None
        joined = join_2022_metrics(districts, ipc)
        self.assertTrue(pd.isna(joined.loc[1, "phase3plus_percent_current"]))
        self.assertTrue(pd.isna(joined.loc[1, "under18_phase3plus_exposure_proxy_2022"]))
        self.assertTrue(pd.isna(joined.loc[2, "under18_phase3plus_exposure_proxy_2022"]))

    def test_join_rejects_wrong_analysis_period(self):
        districts, ipc = inputs()
        ipc.loc[1, "current_to"] = "2026-12-31"
        with self.assertRaisesRegex(ValueError, "current period"):
            join_2022_metrics(districts, ipc)

    def test_render_maps_produces_separate_pngs(self):
        districts, ipc = inputs()
        joined = join_2022_metrics(districts, ipc)
        with TemporaryDirectory(dir=Path(__file__).parent) as directory:
            outputs = render_maps(joined, Path(directory))
            self.assertEqual(len(outputs), 2)
            self.assertTrue(all(p.exists() and p.stat().st_size > 1000 for p in outputs))
            self.assertNotEqual(outputs[0], outputs[1])


if __name__ == "__main__":
    unittest.main()
