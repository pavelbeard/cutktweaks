import os.path
import zipfile
import aiofiles
from fastapi import APIRouter, Depends
from fastapi_csrf_protect import CsrfProtect
from starlette.requests import Request
from starlette.responses import FileResponse
import settings
from settings import templates
from .logic import excel_files_handler, zipfiles
from .exceptions import EmptyDirectory, ForbiddenExtention, EmptyDateTime

okr_router = APIRouter()

app_version = settings.APP_VERSION


@okr_router.get("/okr/excel_load_form")
async def excel_load_form(request: Request, csrf_protect: CsrfProtect = Depends()):
    csrf_token = csrf_protect.generate_csrf()
    response = templates.TemplateResponse("okr/forms/upload_files.html", {
        'request': request, 'csrf_token': csrf_token, "app_version": app_version
    })
    return response


@okr_router.post("/okr/excel_handler")
async def excel_handler(request: Request, csrf_protect: CsrfProtect = Depends()):
    csrf_token = csrf_protect.generate_csrf()

    old_files_files = os.listdir("files")
    if len(old_files_files) > 0:
        for file in old_files_files:
            os.remove(os.path.join("files", file))

    try:
        form = await request.form()
        files = form.getlist('files')
        path = os.path.join(os.getcwd(), "files")
        dt = form['datetime']

        if len(files) == 0:
            raise EmptyDirectory("Файлы не отправлены.")

        if dt is None or dt == '':
            raise EmptyDateTime("Не введен период.")

        paths = []

        if not all([file for file in files if file.filename.split(".")[1] == "xls"]):
            raise ForbiddenExtention("Не xls файлы не обрабатываются.")

        for file in files:
            dest_file_path = os.path.join(path, file.filename)
            paths.append(dest_file_path)

            async with aiofiles.open(dest_file_path, 'wb') as out_file:
                while content := await file.read(1024):
                    await out_file.write(content)

        old_files_download = os.listdir("download")

        if len(old_files_download) > 0:
            for file in old_files_download:
                os.remove(os.path.join("download", file))

        await excel_files_handler(paths, current_period=dt)

        response = templates.TemplateResponse("okr/forms/download.html", {
            'request': request, 'csrf_token': csrf_token, "app_version": app_version
        })
        return response
    except (EmptyDirectory, EmptyDateTime, ForbiddenExtention, FileNotFoundError) as e:
        err_response = templates.TemplateResponse("okr/forms/upload_files.html", {
            'request': request, 'csrf_token': csrf_token, "err": e, "app_version": app_version
        })
        return err_response


@okr_router.get("/okr/download")
async def download(request: Request):
    downloads_path = os.path.join(os.getcwd(), "download")
    files_list = os.listdir(downloads_path)

    files = []

    for f in files_list:
        if f.split(".")[1] != "zip":
            files.append({'file': os.path.join(downloads_path, f)})

    zippath = os.path.join(downloads_path, "Result.zip")
    await zipfiles(zipname=zippath, files=files)

    return FileResponse(path=zippath, filename="Result.zip", media_type="application/octet-stream")
