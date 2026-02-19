import pytest
import requests

from hoofpilot.models.tinygrad_ref import get_tinygrad_ref
from hoofpilot.models.fetcher import ModelFetcher


def fetch_tinygrad_ref():
  try:
    response = requests.get(ModelFetcher.MODEL_URL, timeout=10)
    response.raise_for_status()
    json_data = response.json()
    return json_data.get("tinygrad_ref")
  except (requests.RequestException, ValueError) as e:
    pytest.skip(f"Failed to fetch remote tinygrad_ref: {e}")


def test_tinygrad_ref():
  pytest.skip("tinygrad_ref compatibility check phased out; test skipped.")
