from ninja import Schema
from typing import *

class Settings(Schema):
    maintenance_mode: bool
    maintenance_message: Optional[str]
    app_version: str
    force_update: bool