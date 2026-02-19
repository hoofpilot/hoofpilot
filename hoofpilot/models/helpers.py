"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import hashlib
import os
import pickle
import json
import urllib.request
import shutil
import numpy as np
from openpilot.common.params import Params
from cereal import custom
from hoofpilot.modeld.constants import Meta, MetaTombRaider, MetaSimPose
from hoofpilot.modeld.runners import ModelRunner
from openpilot.system.hardware import PC
from openpilot.system.hardware.hw import Paths
from pathlib import Path


# see the README.md for more details on the model selector versioning
CURRENT_SELECTOR_VERSION = 1
REQUIRED_MIN_SELECTOR_VERSION = 1

USE_ONNX = os.getenv('USE_ONNX', PC)

CUSTOM_MODEL_PATH = Paths.model_root()
MODELS_JSON_PATH = os.path.join(os.path.dirname(__file__), '../../../models/driving_models.json')
MODELS_CACHE_PATH = os.path.join(CUSTOM_MODEL_PATH, 'cache')
METADATA_PATH = Path(__file__).parent / '../models/supercombo_metadata.pkl'
os.makedirs(MODELS_CACHE_PATH, exist_ok=True)

ModelManager = custom.ModelManagerSP

def fetch_and_cache_file(url, sha256, out_path):
  """Download file from url to out_path and verify sha256."""
  if os.path.exists(out_path):
    if verify_file_sync(out_path, sha256):
      return out_path
    else:
      os.remove(out_path)
  with urllib.request.urlopen(url) as response, open(out_path, 'wb') as out_file:
    shutil.copyfileobj(response, out_file)
  if not verify_file_sync(out_path, sha256):
    os.remove(out_path)
    raise RuntimeError(f"Hash mismatch for {out_path}")
  return out_path

def verify_file_sync(file_path: str, expected_hash: str) -> bool:
  if not os.path.exists(file_path):
    return False
  sha256_hash = hashlib.sha256()
  with open(file_path, "rb") as file:
    for chunk in iter(lambda: file.read(4096), b""):
      sha256_hash.update(chunk)
  return sha256_hash.hexdigest().lower() == expected_hash.lower()

def get_model_bundle_from_json():
  """Return the selected model bundle from the models JSON, or None."""
  if not os.path.exists(MODELS_JSON_PATH):
    return None
  with open(MODELS_JSON_PATH, encoding='utf-8') as f:
    models_json = json.load(f)
  # Pick the first compatible bundle (could be improved to select by params)
  for bundle in models_json.get('bundles', []):
    min_ver = bundle.get('minimum_selector_version')
    if min_ver is None:
      min_ver = bundle.get('minimumSelectorVersion')
    if min_ver is not None and int(min_ver) <= CURRENT_SELECTOR_VERSION:
      return bundle
  return None

def fetch_and_cache_model_files(bundle):
  """Download and cache model and metadata files for the bundle, return their paths."""
  model = bundle['models'][0]  # Assume supercombo is first
  art = model['artifact']
  meta = model['metadata']
  art_path = os.path.join(MODELS_CACHE_PATH, art['file_name'])
  meta_path = os.path.join(MODELS_CACHE_PATH, meta['file_name'])
  fetch_and_cache_file(art['download_uri']['url'], art['download_uri']['sha256'], art_path)
  fetch_and_cache_file(meta['download_uri']['url'], meta['download_uri']['sha256'], meta_path)
  return art_path, meta_path


async def verify_file(file_path: str, expected_hash: str) -> bool:
  """Verifies file hash against expected hash"""
  if not os.path.exists(file_path):
    return False

  sha256_hash = hashlib.sha256()
  with open(file_path, "rb") as file:
    for chunk in iter(lambda: file.read(4096), b""):
      sha256_hash.update(chunk)

  return sha256_hash.hexdigest().lower() == expected_hash.lower()


def is_bundle_version_compatible(bundle: dict) -> bool:
  """
  Checks whether the model bundle is compatible with the current selector version constraints.

  The bundle specifies a `minimum_selector_version`, which defines the minimum selector version
  required to load the model. This function ensures that:

    1. The model is not too old: the bundle must require at least `REQUIRED_MIN_SELECTOR_VERSION`.
    2. The model is not too new: it must support the current selector version (`CURRENT_SELECTOR_VERSION`).

  This allows the selector to enforce both a minimum and maximum range of supported models,
  even if a model would otherwise be compatible.

  :param bundle: Dictionary containing `minimum_selector_version`, as defined by the model bundle.
  :type bundle: Dict
  :return: True if the selector version is within the accepted range for the bundle; otherwise False.
  :rtype: Bool
  """
  min_ver = bundle.get("minimumSelectorVersion") or bundle.get("minimum_selector_version", 0)
  return bool(REQUIRED_MIN_SELECTOR_VERSION <= int(min_ver or 0) <= CURRENT_SELECTOR_VERSION)



from typing import Optional

def get_active_bundle(params: Params = None) -> Optional[dict]:
  """Gets the active model bundle from params cache, or selects from JSON and caches it."""
  if params is None:
    params = Params()
  try:
    if (active_bundle := params.get("ModelManager_ActiveBundle") or {}) and is_bundle_version_compatible(active_bundle):
      return active_bundle
  except Exception:
    pass
  # Fallback: select from JSON and cache
  bundle = get_model_bundle_from_json()
  if bundle:
    params.put("ModelManager_ActiveBundle", bundle)
    return bundle
  return None


def get_active_model_runner(params: Params = None, force_check=False) -> custom.ModelManagerSP.Runner:
  """
  Determines and returns the active model runner type, based on provided parameters.
  The function utilizes caching to prevent redundant calculations and checks.

  If the cached "ModelRunnerTypeCache" exists in the provided parameters and `force_check`
  is set to False, the cached value is directly returned. Otherwise, the function determines
  the runner type based on the active model bundle. If a model bundle containing a drive
  model exists, the runner type is derived based on the filename of the drive model.
  Finally, it updates the cache with the determined runner type, if needed.

  :param params: The parameter set used to retrieve caching and runner details. If `None`,
      a default `Params` instance is created internally.
  :type params: Params
  :param force_check: A flag indicating whether to bypass cached results and always
      re-determine the runner type. Defaults to `False`.
  :type force_check: bool
  :return: The determined or cached model runner type.
  :rtype: custom.ModelManagerSP.Runner
  """
  if params is None:
    params = Params()

  if (cached_runner_type := params.get("ModelRunnerTypeCache")) and not force_check:
    if isinstance(cached_runner_type, str) and cached_runner_type.isdigit():
      return int(cached_runner_type)

  runner_type = custom.ModelManagerSP.Runner.stock

  if active_bundle := get_active_bundle(params):
    runner_str = active_bundle.get('runner', 'stock') if isinstance(active_bundle, dict) else active_bundle.runner.raw
    runner_type = getattr(custom.ModelManagerSP.Runner, runner_str, custom.ModelManagerSP.Runner.stock)

  if cached_runner_type != runner_type:
    params.put("ModelRunnerTypeCache", int(runner_type))

  return runner_type


# New model fetcher logic for new repo structure
def get_model_path():
  if USE_ONNX:
    return {ModelRunner.ONNX: Path(__file__).parent / '../models/supercombo.onnx'}
  bundle = get_active_bundle()
  if bundle:
    art_path, _ = fetch_and_cache_model_files(bundle)
    return {ModelRunner.THNEED: art_path}
  return {ModelRunner.THNEED: Path(__file__).parent / '../models/supercombo.thneed'}

def load_metadata():
  bundle = get_active_bundle()
  if bundle:
    _, meta_path = fetch_and_cache_model_files(bundle)
    with open(meta_path, 'rb') as f:
      return pickle.load(f)
  # fallback
  with open(METADATA_PATH, 'rb') as f:
    return pickle.load(f)


def prepare_inputs(model_metadata) -> dict[str, np.ndarray]:
  # img buffers are managed in openCL transform code so we don't pass them as inputs
  inputs = {
    k: np.zeros(v, dtype=np.float32).flatten()
    for k, v in model_metadata['input_shapes'].items()
    if 'img' not in k
  }

  return inputs


def load_meta_constants(model_metadata):
  """
  Determines and loads the appropriate meta model class based on the metadata provided. The function checks
  specific keys and conditions within the provided metadata dictionary to identify the corresponding meta
  model class to return.

  :param model_metadata: Dictionary containing metadata about the model. It includes
      details such as input shapes, output slices, and other configurations for identifying
      metadata-dependent meta model classes.
  :type model_metadata: dict
  :return: The appropriate meta model class (Meta, MetaSimPose, or MetaTombRaider)
      based on the conditions and metadata provided.
  :rtype: type
  """
  meta = Meta  # Default Meta

  if 'sim_pose' in model_metadata['input_shapes'].keys():
    # Meta for models with sim_pose input
    meta = MetaSimPose
  else:
    # Meta for Tomb Raider, it does not include sim_pose input but has the same meta slice as previous models
    meta_slice = model_metadata['output_slices']['meta']
    meta_tf_slice = slice(5868, 5921, None)

    if (
            meta_slice.start == meta_tf_slice.start and
            meta_slice.stop == meta_tf_slice.stop and
            meta_slice.step == meta_tf_slice.step
    ):
      meta = MetaTombRaider

  return meta


# The following method(s) are modeld helper methods
def plan_x_idxs_helper(constants, plan, model_output) -> list[float]:
  # times at X_IDXS according to plan.
  LINE_T_IDXS = [np.nan] * constants.IDX_N
  LINE_T_IDXS[0] = 0.0
  plan_x = model_output['plan'][0, :, plan.POSITION][:, 0].tolist()
  for xidx in range(1, constants.IDX_N):
    tidx = 0
    # increment tidx until we find an element that's further away than the current xidx
    while tidx < constants.IDX_N - 1 and plan_x[tidx + 1] < constants.X_IDXS[xidx]:
      tidx += 1
    if tidx == constants.IDX_N - 1:
      # if the plan doesn't extend far enough, set plan_t to the max value (10s), then break
      LINE_T_IDXS[xidx] = constants.T_IDXS[constants.IDX_N - 1]
      break
    # interpolate to find `t` for the current xidx
    current_x_val = plan_x[tidx]
    next_x_val = plan_x[tidx + 1]
    p = (constants.X_IDXS[xidx] - current_x_val) / (next_x_val - current_x_val) if abs(
      next_x_val - current_x_val) > 1e-9 else float('nan')
    LINE_T_IDXS[xidx] = p * constants.T_IDXS[tidx + 1] + (1 - p) * constants.T_IDXS[tidx]
  return LINE_T_IDXS

