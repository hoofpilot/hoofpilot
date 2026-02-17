from hoofpilot import get_file_hash
from hoofpilot.mapd import MAPD_PATH
from hoofpilot.mapd.update_version import MAPD_HASH_PATH


class TestMapdVersion:
  def test_compare_versions(self):
    mapd_hash = get_file_hash(MAPD_PATH)

    with open(MAPD_HASH_PATH) as f:
      current_hash = f.read().strip()

    assert current_hash == mapd_hash, "Run hoofpilot/mapd/update_version.py to update the current mapd version and hash"

