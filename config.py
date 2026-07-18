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
        
        # 🚀 Multiple Images ki array list
        self.START_IMG_URL = [
            "https://te.legra.ph/file/7757731c3e8b784b6a550.png", "https://te.legra.ph/file/58c34981e21180989887c.png", 
            "https://te.legra.ph/file/a3a874be5095d9af685ac.png", "https://te.legra.ph/file/ac461a1889255424420ff.png", 
            "https://te.legra.ph/file/74a8ba5270d0e27ac045c.png", "https://te.legra.ph/file/c0d0ee1452cbbbce116f4.png", 
            "https://te.legra.ph/file/d373ae93502a5ae7fd403.png", "https://te.legra.ph/file/ab243bcad20965f637b5c.png", 
            "https://te.legra.ph/file/fd9cc86239dd76d564d01.png", "https://te.legra.ph/file/c12a0b77178e2d2e27a50.png", 
            "https://te.legra.ph/file/35177bbb5d5f07ad8e394.png", "https://te.legra.ph/file/700af8c3ee786a20aff35.png", 
            "https://te.legra.ph/file/cbecd8af0446a422a95ca.png", "https://te.legra.ph/file/c3a0fde4abde25dd25e26.png", 
            "https://te.legra.ph/file/7be8c2f9e093f695c4c6e.png", "https://te.legra.ph/file/ee10888e828bae3a6a0fc.png", 
            "https://te.legra.ph/file/1b55fe681163188149fa4.png", "https://te.legra.ph/file/30ee4e96f64cd9abb69b6.png", 
            "https://te.legra.ph/file/30b121ce5fa87360692ba.png", "https://te.legra.ph/file/f0617cc52008bd78f1a9d.png", 
            "https://te.legra.ph/file/1cd1adc3eb9ac0a101610.png", "https://te.legra.ph/file/860c3dd149f91eb450d5a.png", 
            "https://te.legra.ph/file/2e9df77f8100e0327ba52.png", "https://te.legra.ph/file/639efe98c133d71c418db.png", 
            "https://te.legra.ph/file/8a834586b677739b86bff.png", "https://te.legra.ph/file/13f79674ce777f43871fb.png", 
            "https://te.legra.ph/file/147157eca055a1e2c8756.png", "https://te.legra.ph/file/b774a8da74dc954afebc6.png", 
            "https://te.legra.ph/file/7ae4a6a6a6c28f9f08ceb.png", "https://te.legra.ph/file/12d5ea64ed00416a38ec8.png"
        ]
        
        self.PING_IMG_URL = self.START_IMG_URL.copy()
        self.STATS_IMG_URL = self.START_IMG_URL.copy()
        
        # Backup variables agar koi purana plugin inko dhoondhe
        self.START_IMG = self.START_IMG_URL
        self.PING_IMG = self.PING_IMG_URL

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
            
