import json
import os
from pathlib import Path

from tinygrad.tensor import Tensor
from tinygrad.helpers import to_mv

MODELS_DIR = Path(__file__).parent.parent / 'models'
COMPILED_FLAGS_PATH = MODELS_DIR / 'tg_compiled_flags.json'


def set_tinygrad_backend_from_compiled_flags() -> None:
  if os.path.isfile(COMPILED_FLAGS_PATH):
    with open(COMPILED_FLAGS_PATH) as f:
      os.environ['DEV'] = str(json.load(f)['DEV'])


def qcom_tensor_from_opencl_address(opencl_address, shape, dtype):
  cl_buf_desc_ptr = to_mv(opencl_address, 8).cast('Q')[0]
  rawbuf_ptr = to_mv(cl_buf_desc_ptr, 0x100).cast('Q')[20]
  return Tensor.from_blob(rawbuf_ptr, shape, dtype=dtype, device='QCOM')
