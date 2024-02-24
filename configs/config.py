import ujson
import models.bot_properties as bot_properties


class Config:
    with open("configs/config.json", mode="r", encoding="utf-8") as _file:
        _data = ujson.load(_file)

    @classmethod
    def get_bot(cls) -> bot_properties.Bot:
        return bot_properties.Bot(token=cls._data["token"])