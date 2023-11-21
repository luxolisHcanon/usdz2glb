from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from fastapi import status, HTTPException
from fastapi import Response
import tempfile
from pathlib import Path
import shutil, tempfile
from pathlib import Path
from config import get_config
from ktx2_compress import ktx2_compression
import bpy
import requests

class ResponseInfo():
    x_access_token: str
    callback_url: str
    organization_id: str
    device_name: str
    lat: str
    lon: str
    session_id: str
    scanning_type_id: str
    subscription_type: str
    firebase_device_token: str
    model_name: str
    model_folder: str

config = get_config();
def convert_usdz_file_to_glb(file_usdz_src, file_glb_dest):
    print("Load USDZ File")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    objs = [ob for ob in bpy.context.scene.objects if ob.type in ('CAMERA', 'MESH')]
    for obj in objs:
        bpy.data.objects.remove(obj)

    # TODO: If file id invalid and cannot be open error is logged to console but not thrown
    if file_usdz_src.suffix == '.usdz':
        bpy.ops.wm.usd_import("EXEC_DEFAULT", filepath=str(file_usdz_src))
    elif file_usdz_src.suffix == '.gltf':
        bpy.ops.import_scene.gltf(filepath=str(file_usdz_src))
    elif file_usdz_src.suffix == '.obj':
        bpy.ops.import_scene.obj(
            filepath=str(file_usdz_src)
        )
    elif file_usdz_src.suffix == '.zip':
        folder_unpacked = Path(file_usdz_src).with_suffix('')
        shutil.unpack_archive(
            filename=file_usdz_src,
            extract_dir=folder_unpacked,
        )
        print(folder_unpacked)
        if len(list(folder_unpacked.glob('**/*.gltf')))>0:
            gltf_file = list(folder_unpacked.glob('**/*.gltf'))[0]
            print("Detected GLTF, at", folder_unpacked)
            bpy.ops.import_scene.gltf(filepath=str(gltf_file))
        elif len(list(folder_unpacked.glob('**/*.obj')))>0:
            obj_file = list(folder_unpacked.glob('**/*.obj'))[0]
            bpy.ops.import_scene.obj(
                filepath=str(obj_file)
            )
        else:
            raise HTTPException(detail=f"Provided zip file didn't have gltf or obj files in it {list(folder_unpacked.glob('*'))}.",status_code=500)

    print("Save GLB File")
    # TODO: Clear blender to save memory (if needed)
    bpy.ops.export_scene.gltf(
        filepath=str(file_glb_dest),
        export_format="GLB",
        export_draco_mesh_compression_enable=True,
        export_draco_position_quantization=config.QUANTIZATION
    )

async def convert_usdz_upload_glb(url_download, url_upload, upload_ktx2_url):

    print("Downloading USDZ File")
    # download file
    sess = Path(tempfile.mkdtemp())
    filename = 'upload.usdz'
    file_usdz = sess / filename
    file_usdz.write_bytes(requests.get(url_download).content)

    filename = 'upload.glb'
    file_glb = sess / filename

    print("Convert USDZ File")
    # Convert usdz file to glb file
    convert_usdz_file_to_glb(file_usdz, file_glb);

    print("Upload GLB File")
    # Upload file
    upload_result = requests.put(
        url_upload,
        data=open(file_glb, 'rb'),
        headers={
            'Content-Type': 'application/octet-stream',
        });

    print("Run ktx2 compression")
    # Compress glb file using ktx2
    filename = 'upload_compressed.glb'
    file_glb_compressed = sess / filename
    upload_File = ktx2_compression(file_glb, file_glb_compressed)

    print("Upload ktx2 File")
    # Upload file
    upload_result = requests.put(
        upload_ktx2_url,
        data=open(upload_File, 'rb'),
        headers={
            'Content-Type': 'application/octet-stream',
        });

    return upload_result.status_code


# TODO: Handle errors?
async def convert_and_send_confirmation(url_download, url_upload, upload_ktx2_url, response_payload:ResponseInfo):
    await convert_usdz_upload_glb(url_download, url_upload, upload_ktx2_url)

    # Send Response
    payload = {
        "organizationID": response_payload.organization_id if response_payload.organization_id else None,
        "deviceName": response_payload.device_name if response_payload.device_name else None,
        "sessionID": response_payload.session_id,
        "scanningTypeID": response_payload.scanning_type_id,
        "subscriptionType": response_payload.subscription_type,
        "firebaseDeviceToken": response_payload.firebase_device_token,
        "lat": response_payload.lat,
        "lon": response_payload.lon,
        "modelName": response_payload.model_name,
        "modelFolder": response_payload.model_folder
    }

    print("Hit callback")
    print(response_payload.model_name)
    print(response_payload.callback_url)
    headers = {"x-access-token": response_payload.x_access_token}
    res = requests.post(response_payload.callback_url, headers=headers, data=payload)
    print(res)
