from ninja import Schema

class WebGameSchema(Schema):
    id: int
    name: str
    description:str
    bg_image:str
    game_image:str
    live: bool
    playstore_url:str
    appstore_url: str

class ContactSchema(Schema):
    name: str
    message: str
    email: str
    phone: str