from backend.providers.comfyui.provider import ComfyUIProvider
from backend.providers.jimeng.provider import JimengProvider
from backend.providers.kling.provider import KlingProvider

PROVIDERS = {
    "comfyui": ComfyUIProvider(),
    "jimeng": JimengProvider(),
    "kling": KlingProvider(),
}
