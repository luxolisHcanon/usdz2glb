import time
import pytest, tempfile, shutil
from pathlib import Path

res_p = Path(f'store/gen/{time.time_ns()//1000}')
res_p.mkdir(parents=True,exist_ok=True)

@pytest.mark.parametrize("file", [
    Path("store/sneaker_airforce.usdz"),
    Path("store/Fox/glTF"),
    Path("store/LibertyStatue"),
    Path("store/scene.gltf"),
    Path("store/LibertyStatue"),
    Path("store/LibertyStatue/LibertStatue.obj"),
])
def test_main(tmp_path: Path, file:Path):
    from fastapi.testclient import TestClient
    from main import app

    with TestClient(app) as client:
        if file.suffix == '':
            upload = Path(shutil.make_archive(tmp_path / 'pack', 'zip', file))
        else:
            upload = file
        assert upload.exists()
        resp = client.post("/convert", 
            files={"file": (upload.name, upload.open("rb"))})
        assert resp.status_code == 200
        res = res_p/f'{file.name.lower()}-down.glb'
        res.write_bytes(resp.content)
        print("FILE HERE >>>>>>>>>>>",res)

        
urls = [
    "https://storage.googleapis.com/tornikeo-portfolio-cdn/sneaker_airforce.usdz",
    'https://openair3d-prod.s3.us-east-2.amazonaws.com/data/174/models/object/1000/object3d.usdz?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIA5A4UAIRZ3TLUF6XT%2F20230512%2Fus-east-2%2Fs3%2Faws4_request&X-Amz-Date=20230512T124408Z&X-Amz-Expires=18000&X-Amz-Signature=8c6d84ab98137be8d1ac44adfc9122a7a9699fbe443591e940bf8de8093e3ac3&X-Amz-SignedHeaders=host'
]

put_urls = [
    'https://openair3d-dev.s3.us-east-2.amazonaws.com/data/174/models/object/1000/object3d.glb?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIA5A4UAIRZ4YF5RYYO%2F20230512%2Fus-east-2%2Fs3%2Faws4_request&X-Amz-Date=20230512T213547Z&X-Amz-Expires=18000&X-Amz-Signature=5d3f5c298324ea6b8bcef29f7052de5325e41ee8ee5ff0660fb04e01fd77596e&X-Amz-SignedHeaders=host'
]

@pytest.mark.parametrize("url", urls)
def test_from_url(tmp_path: Path, url:str):
    from fastapi.testclient import TestClient
    from main import app

    with TestClient(app) as client:
        resp = client.post("/convert-from-url", 
            json={"url": url}
        )
        assert resp.status_code == 200
        res = res_p/f'{time.time_ns()}-down.glb'
        res.write_bytes(resp.content)
        print("FILE HERE >>>>>>>>>>>",res)



@pytest.mark.parametrize("url,upload_url", zip(urls, put_urls), )
def test_from_url_to_url(tmp_path: Path, url:str,upload_url:str):
    from fastapi.testclient import TestClient
    from main import app

    with TestClient(app) as client:
        resp = client.post("/convert-from-url-to-url", 
            json={"url": url, 'upload_url':upload_url}
        )
        assert resp.status_code == 200
        res = res_p/f'{time.time_ns()}-down.glb'
        res.write_bytes(resp.content)
        print("FILE HERE >>>>>>>>>>>",res)
