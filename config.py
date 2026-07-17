from os import getenv
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self):
        # 1. API ID & HASH (Defaults diye hain, par env se overwrite ho jayenge)
        self.API_ID = int(getenv("API_ID", "17596251"))
        self.API_HASH = getenv("API_HASH", "e58343b4c0193e293e391daf97603fcd")

        # 2. BOT DETAILS & DB
        self.BOT_TOKEN = getenv("BOT_TOKEN")
        self.MONGO_URL = getenv("MONGO_URL")

        # 3. IDS (Defaults ko 0 rakha hai taaki ValueError na aaye)
        self.LOGGER_ID = int(getenv("LOGGER_ID", "0"))
        self.OWNER_ID = int(getenv("OWNER_ID", "0"))
        
        # 4. SESSIONS (Koi default text nahi dala, taki seedha catch ho sake)
        self.SESSION1 = getenv("SESSION")
        self.SESSION2 = getenv("SESSION2")
        self.SESSION3 = getenv("SESSION3")

        # 5. CHANNELS
        self.SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/TuneBots")
        self.SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/betabot_support")
        self.OWNER_USERNAME = getenv("OWNER_USERNAME", "https://t.me/ll_Alexx_lll")

        # 6. PLAY SETTINGS
        self.AUTO_END: bool = getenv("AUTO_END", "False").lower() == "true"
        self.AUTO_LEAVE: bool = getenv("AUTO_LEAVE", "False").lower() == "true"
        self.VIDEO_PLAY: bool = getenv("VIDEO_PLAY", "True").lower() == "true"

        # 7. LIMITS & KEYS
        self.QUEUE_LIMIT = int(getenv("QUEUE_LIMIT", "200"))
        self.DURATION_LIMIT = int(getenv("DURATION_LIMIT", "17000"))
        self.PLAYLIST_LIMIT = int(getenv("PLAYLIST_LIMIT", "200"))
        self.YOUTUBE_API_KEY = getenv("YOUTUBE_API_KEY", "INFLEX86759628D")
        
        # 8. IMAGES
        self.DEFAULT_THUMB = getenv("DEFAULT_THUMB", "https://te.legra.ph/file/3e40a408286d4eda24191.jpg")
        self.PING_IMG = getenv("PING_IMG", "https://n.uguu.se/nKCUOshT.jpg")
        self.START_IMG = getenv("START_IMG", "https://d.uguu.se/nGpQVVqm.jpg")

    def check(self):
        missing = []
        # Jo variables zaroori hain, unhe check karega
        if not self.BOT_TOKEN: missing.append("BOT_TOKEN")
        if not self.MONGO_URL: missing.append("MONGO_URL")
        if not self.SESSION1: missing.append("SESSION (Session 1)")
        if self.LOGGER_ID == 0: missing.append("LOGGER_ID")
        if self.OWNER_ID == 0: missing.append("OWNER_ID")

        if missing:
            raise SystemExit(f"⚠️ ERROR: Tumhare environment vars mein ye missing hain: {', '.join(missing)}")
            
