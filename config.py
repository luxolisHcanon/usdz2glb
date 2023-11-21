
import os
from pathlib import Path
from pydantic import BaseModel, BaseSettings

class Config(BaseSettings):
   
    GLTFPACK: str = (
        Path(__file__).parent.resolve().as_posix() + "/binaries/gltfpack"
    )

    # DRACO COMPRESSION SETTINGS, Quantize to x number of bits, higher value seems to result in better looking compressed models
    QUANTIZATION: int = 18


def get_config():
    return Config()
