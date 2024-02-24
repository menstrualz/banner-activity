from enum import Enum, IntEnum


class GuildId(IntEnum):
    GUILD = 1104144898157981760 #ID сервера


class BannerConstants(Enum):
    AVATAR_SIZE = (250, 250) #размер аватара
    AVATAR_POSITION = (65, 217) #позиция аватара
    FONT_MAIN_SIZE = 32 #размер шрифта
    FONT_NAME_SIZE = 54 #размер шрифта
    MEMBER_TOTAL_POSITION = (576, 245) #позиция количества участников
    VOICE_TOTAL_POSITION = (853, 395) #позиция количества участников в голосовом канале
    ACTIVE_USER_NAME_POSITION = (477, 309) #позиция имени активного участника
    BANNER_UPDATE_INTERVAL = 120  #в минутах
