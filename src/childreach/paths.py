"""Reusable filesystem paths for the ChildReach project.

Keep notebooks independently runnable by importing these constants instead of
copying path strings between notebooks. Analysis outputs should still be loaded
from saved files in data/processed, not shared through notebook memory.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
DATA_RAW = DATA_DIR / "raw"
DATA_INTERIM = DATA_DIR / "interim"
DATA_PROCESSED = DATA_DIR / "processed"
FIGURES_DIR = PROJECT_ROOT / "figures"
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"
SRC_DIR = PROJECT_ROOT / "src"

GEBOUNDARIES_ADM2_METADATA_URL = "https://www.geoboundaries.org/api/current/gbOpen/MOZ/ADM2/"
GEBOUNDARIES_ADM2_GEOJSON_URL = (
    "https://github.com/wmgeolab/geoBoundaries/raw/9469f09/releaseData/"
    "gbOpen/MOZ/ADM2/geoBoundaries-MOZ-ADM2.geojson"
)

BOUNDARIES_RAW_DIR = DATA_RAW / "boundaries"
WORLDPOP_RAW_DIR = DATA_RAW / "worldpop"
WORLDPOP_UNDER18_2019_DIR = WORLDPOP_RAW_DIR / "moz_under_age_18_2019"

ADM2_BOUNDARIES_GEOJSON = BOUNDARIES_RAW_DIR / "geoBoundaries-MOZ-ADM2.geojson"
WORLDPOP_UNDER18_TOTAL_2019_TIF = (
    WORLDPOP_UNDER18_2019_DIR / "moz_T_Under_18_2019_CN_100m_R2025A_v1.tif"
)

MOZ_ADM2_UNDER18_2019_LAYER = "moz_adm2_under18_2019"
MOZ_ADM2_UNDER18_2019_GPKG = DATA_PROCESSED / "moz_adm2_under18_2019.gpkg"
MOZ_ADM2_UNDER18_2019_CSV = DATA_PROCESSED / "moz_adm2_under18_2019.csv"
MOZ_ADM2_UNDER18_2019_CHOROPLETH = FIGURES_DIR / "moz_adm2_under18_2019_choropleth.png"
MOZ_ADM2_BOUNDARIES_PREVIEW = FIGURES_DIR / "moz_adm2_boundaries_preview.png"
