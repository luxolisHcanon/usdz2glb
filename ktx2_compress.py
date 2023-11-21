import subprocess
from config import get_config

config = get_config()
def ktx2_compression(input_file, out_file):
    if True:
        compress_texture_cmd = (
            config.GLTFPACK
            + " -i "
            + str(input_file)
            + " -o "
            + str(out_file)
            + " -tc"
        )
        try:
            result = subprocess.run([compress_texture_cmd], capture_output=True, text=True, shell=True)
            if result.stderr:
                print(f"error: {result.stderr}")
                return input_file

            return out_file
        except Exception as error:
            print(f"texture compression error: {error}")
    return input_file