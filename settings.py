from fastapi_csrf_protect import CsrfProtect
from pydantic import BaseModel
from starlette.templating import Jinja2Templates


templates = Jinja2Templates(directory="templates")


class CSRFSettings(BaseModel):
    secret_key: str = '3LlPp6V-MA_2Wdb8p3K4l3I4Y-onPqRZMQ9IfSigZos='


@CsrfProtect.load_config
def get_csrf_config():
    return CSRFSettings()



