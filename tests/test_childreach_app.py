"""Focused saved-data dashboard checks; Streamlit is imported only by main()."""

import importlib.util
from pathlib import Path
import unittest

import geopandas as gpd
import pandas as pd
from shapely.geometry import box

APP = Path(__file__).resolve().parents[1] / "app" / "childreach_app.py"
spec = importlib.util.spec_from_file_location("childreach_app", APP)
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)


class DashboardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = app.load_data()

    def test_saved_inputs_join_by_shapeid_and_keep_temporal_scope(self):
        data = self.data
        csv = pd.read_csv(app.IPC_CSV, dtype={"shapeID": str}).set_index("shapeID")
        self.assertEqual(set(data.shapeID), set(csv.index))
        for row in data.itertuples():
            original = csv.loc[row.shapeID]
            if pd.isna(original[app.PROXY]):
                self.assertTrue(pd.isna(getattr(row, app.PROXY)))
            else:
                self.assertAlmostEqual(getattr(row, app.PROXY), original[app.PROXY], places=4)
        self.assertEqual(set(data.loc[data[app.PERCENT].notna(), "current_from"]), {"2022-10-01"})
        self.assertEqual(set(data.loc[data[app.PERCENT].notna(), "current_to"]), {"2023-03-31"})

    def test_coverage_missing_and_zero_differ(self):
        frame = pd.DataFrame({app.PROXY: [0, None, 12]})
        self.assertEqual(app.coverage(frame, app.PROXY), (2, 1, 3))

    def test_rank_only_comparable_proxy(self):
        frame = pd.DataFrame({"shapeID": ["b", "a", "c", "d"],
                              "shapeName": ["B", "A", "C", "D"],
                              app.PROXY: [0, None, 12, 12]})
        self.assertEqual(app.top_proxy(frame, 2).shapeID.tolist(), ["c", "d"])
        self.assertEqual(app.top_proxy(frame, 4).shapeID.tolist(), ["c", "d", "b"])

    def test_selector_uses_distinct_shapeids_for_identical_names(self):
        frame = pd.DataFrame({"shapeID": ["a", "b"], "shapeName": ["Same", "Same"]})
        self.assertEqual(app.district_options(frame), {"a": "Same · a", "b": "Same · b"})

    def test_map_renders_missing_hatch_and_selection_without_streamlit(self):
        data = gpd.GeoDataFrame({"shapeID": ["a", "b"], "shapeName": ["A", "B"],
                                 app.PROXY: [0, None]},
                                geometry=[box(0, 0, 1, 1), box(1, 0, 2, 1)], crs="EPSG:4326")
        fig = app.draw_map(data, app.PROXY, "b")
        try:
            self.assertTrue(any(collection.get_hatch() for ax in fig.axes for collection in ax.collections))
            self.assertTrue(any(2.2 in collection.get_linewidths() for ax in fig.axes
                                for collection in ax.collections))
        finally:
            app.plt.close(fig)


if __name__ == "__main__":
    unittest.main()
