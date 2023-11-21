from fastapi import FastAPI, BackgroundTasks, File, UploadFile
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
from pydantic import BaseModel
from service import convert_usdz_upload_glb, convert_and_send_confirmation, ResponseInfo;
from task_queue import get_task_queue, get_job_information

app = FastAPI(debug=True)
config = get_config()

class UrlToUrlRequest(BaseModel):
    url: str
    upload_url: str
    upload_ktx2_url: str

class UrlToUrlQueueRequest(BaseModel):
    to_convert_url: str
    to_upload_url: str
    to_upload_ktx2_url: str
    x_access_token: str
    callback_url: str
    organization_id: str | None
    device_name: str | None
    lat: str | None
    lon: str | None
    session_id: str
    scanning_type_id: str | None
    subscription_type: str | None
    firebase_device_token: str | None
    model_folder: str | None
    model_name: str

class JobInfoRequest(BaseModel):
    job_id: str

@app.post("/convert-from-url-to-url")
async def create_upload_file(request: UrlToUrlRequest):

    download_url = request.url;
    upload_url = request.upload_url;
    upload_ktx2_url = request.upload_ktx2_url;
    print("STARTED /convert-from-url-to-url")
    print(download_url)
    upload_response = await convert_usdz_upload_glb(download_url, upload_url, upload_ktx2_url);

    return {"success": True, 'upload_response': upload_response }

@app.post("/convert-payload-async")
async def create_upload_file(request: UrlToUrlQueueRequest):

    download_url = request.to_convert_url;
    upload_url = request.to_upload_url;
    upload_ktx2_url = request.to_upload_ktx2_url;
    print("STARTED /convert-payload-async")
    print(download_url)

    payload = ResponseInfo();
    payload.x_access_token = request.x_access_token
    payload.callback_url = request.callback_url
    payload.organization_id = request.organization_id
    payload.device_name = request.device_name
    payload.lat = request.lat
    payload.lon = request.lon
    payload.session_id = request.session_id
    payload.scanning_type_id = request.scanning_type_id
    payload.subscription_type = request.subscription_type
    payload.firebase_device_token = request.firebase_device_token
    payload.model_name = request.model_name
    payload.model_folder = request.model_folder

    print(payload.model_name)

    await convert_and_send_confirmation(download_url, upload_url, upload_ktx2_url, payload)

    # lr_task_queue = get_task_queue()
    # job = lr_task_queue.enqueue(convert_and_send_confirmation, download_url, upload_url, payload)

    return {"success": True, "job_id": 1}

@app.post("/get_job_info")
async def create_upload_file(request: JobInfoRequest):

    job_id = request.job_id

    print(get_job_information(job_id))

    return {"success": True, "job_info": get_job_information(job_id).get_status()}


# TODO: Confirm if below endpoints are required
@app.post("/convert")
async def create_upload_file(file: UploadFile):
    sess = Path(tempfile.mkdtemp())
    contents = await file.read()
    filepath = sess / file.filename
    filepath.write_bytes(contents)
    outfile = sess / filepath.with_suffix(".glb")

    objs = [ob for ob in bpy.context.scene.objects if ob.type in ('CAMERA', 'MESH')]
    for obj in objs:
        bpy.data.objects.remove(obj)

    if filepath.suffix == '.usdz':
        bpy.ops.wm.usd_import("EXEC_DEFAULT", filepath=str(filepath))
    elif filepath.suffix == '.gltf':
        bpy.ops.import_scene.gltf(filepath=str(filepath))
    elif filepath.suffix == '.obj':
        bpy.ops.import_scene.obj(
            filepath=str(filepath)
        )
    elif filepath.suffix == '.zip':
        folder_unpacked = Path(filepath).with_suffix('')
        shutil.unpack_archive(
            filename=filepath,
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

    bpy.ops.export_scene.gltf(
        filepath=str(outfile),
        export_format="GLB",
    )
    return FileResponse(
        outfile,
        filename=outfile.name,
    )

class UrlRequest(BaseModel):
    url: str

@app.post("/convert-from-url")
async def create_upload_file(request: UrlRequest):
    # download file
    sess = Path(tempfile.mkdtemp())
    filename = 'upload.usdz'
    filepath = sess / filename
    filepath.write_bytes(requests.get(request.url).content)

    # contents = await file.read()
    # filepath = sess / file.filename
    # filepath.write_bytes(contents)
    outfile = sess / filepath.with_suffix(".glb")

    bpy.ops.wm.read_factory_settings(use_empty=True)
    objs = [ob for ob in bpy.context.scene.objects if ob.type in ('CAMERA', 'MESH')]
    for obj in objs:
        bpy.data.objects.remove(obj)

    if filepath.suffix == '.usdz':
        bpy.ops.wm.usd_import("EXEC_DEFAULT", filepath=str(filepath))
    elif filepath.suffix == '.gltf':
        bpy.ops.import_scene.gltf(filepath=str(filepath))
    elif filepath.suffix == '.obj':
        bpy.ops.import_scene.obj(
            filepath=str(filepath)
        )
    elif filepath.suffix == '.zip':
        folder_unpacked = Path(filepath).with_suffix('')
        shutil.unpack_archive(
            filename=filepath,
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

    bpy.ops.export_scene.gltf(
        filepath=str(outfile),
        export_format="GLB",
    )
    return FileResponse(
        outfile,
        filename=outfile.name,
    )
