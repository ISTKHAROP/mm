import os
import re
import asyncio
import aiohttp
import yt_dlp
from py_yt import VideosSearch, Playlist
from AloneX import logger, config

API_URL = "https://teaminflex.xyz"
DOWNLOAD_DIR = "downloads"


class YouTube:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = re.compile(
            r"(https?://)?(www\.|m\.|music\.)?"
            r"(youtube\.com/(watch\?v=|shorts/|playlist\?list=)|youtu\.be/)"
            r"([A-Za-z0-9_-]{11}|PL[A-Za-z0-9_-]+)([&?][^\s]*)?"
        )

    # ---------------- basic helpers ----------------

    def valid(self, url: str) -> bool:
        return bool(re.match(self.regex, url))

    async def search(self, query: str, m_id: int, video: bool = False):
        from AloneX.helpers import Track, utils 
        
        try:
            # Search limit 1 hi rakhi hai taki response sabse fast aaye
            _search = VideosSearch(query, limit=1)
            results = await _search.next()
            if results and results["result"]:
                data = results["result"][0]
                return Track(
                    id=data.get("id"),
                    channel_name=data.get("channel", {}).get("name"),
                    duration=data.get("duration"),
                    duration_sec=utils.to_seconds(data.get("duration")) if data.get("duration") else 0,
                    message_id=m_id,
                    title=data.get("title")[:25],
                    thumbnail=data.get("thumbnails", [{}])[-1].get("url").split("?")[0],
                    url=data.get("link"),
                    view_count=data.get("viewCount", {}).get("short"),
                    video=video,
                )
        except Exception as e:
            logger.error(f"Search error: {e}")
        return None

    async def playlist(self, limit: int, user: str, url: str, video: bool):
        from AloneX.helpers import Track, utils
        
        tracks = []
        try:
            plist = await Playlist.get(url)
            for data in plist.get("videos", [])[:limit]:
                track = Track(
                    id=data.get("id"),
                    channel_name=data.get("channel", {}).get("name", ""),
                    duration=data.get("duration"),
                    duration_sec=utils.to_seconds(data.get("duration")) if data.get("duration") else 0,
                    title=data.get("title")[:25],
                    thumbnail=data.get("thumbnails", [{}])[-1].get("url").split("?")[0],
                    url=data.get("link").split("&list=")[0],
                    user=user,
                    view_count="",
                    video=video,
                )
                tracks.append(track)
        except Exception as e:
            logger.error(f"Playlist error: {e}")
        return tracks

    # ---------------- download (teaminflex.xyz API) ----------------

    async def download(self, video_id: str, video: bool = False) -> str | None:
        if not video_id or len(video_id) < 3:
            return None

        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        ext = "mkv" if video else "webm"
        file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.{ext}")

        if os.path.exists(file_path):
            return file_path

        max_retries = 3
        retry_delay = 1  
        transient_statuses = {502, 503, 504}

        for attempt in range(1, max_retries + 1):
            try:
                # 🚀 SPEED UP: TCPConnector use kiya taki connections fast establish hon
                connector = aiohttp.TCPConnector(limit=50, enable_cleanup_closed=True)
                async with aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=45), # Timeout 60s se 45s kiya
                    connector=connector
                ) as session:
                    payload = {"url": video_id, "type": "video" if video else "audio"}
                    headers = {
                        "Content-Type": "application/json",
                        "X-API-KEY": config.YOUTUBE_API_KEY
                    }

                    async with session.post(f"{API_URL}/download", json=payload, headers=headers) as response:
                        if response.status == 401:
                            logger.error("[API] Invalid API key")
                            return None

                        if response.status in transient_statuses:
                            if attempt < max_retries:
                                await asyncio.sleep(retry_delay)
                                continue
                            return None

                        if response.status != 200:
                            return None

                        try:
                            data = await response.json()
                        except Exception:
                            if attempt < max_retries:
                                await asyncio.sleep(retry_delay)
                                continue
                            return None

                        if data.get("status") != "success" or not data.get("download_url"):
                            if attempt < max_retries:
                                await asyncio.sleep(retry_delay)
                                continue
                            return None

                        download_link = f"{API_URL}{data['download_url']}"

                    async with session.get(download_link) as file_response:
                        if file_response.status in transient_statuses or file_response.status != 200:
                            if attempt < max_retries:
                                await asyncio.sleep(retry_delay)
                                continue
                            return None

                        with open(file_path, "wb") as f:
                            # 🚀 SPEED UP: Chunk size 8192 (8KB) se 1048576 (1MB) kar diya. 
                            # Isse downloading directly disk par fast likhi jayegi.
                            async for chunk in file_response.content.iter_chunked(1048576):
                                f.write(chunk)

                if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                    return file_path

                if os.path.exists(file_path):
                    try: os.remove(file_path)
                    except: pass
                if attempt < max_retries:
                    await asyncio.sleep(retry_delay)
                    continue
                return None

            except (aiohttp.ClientError, asyncio.TimeoutError):
                if os.path.exists(file_path):
                    try: os.remove(file_path)
                    except: pass
                if attempt < max_retries:
                    await asyncio.sleep(retry_delay)
                    continue
                return None

            except Exception:
                if os.path.exists(file_path):
                    try: os.remove(file_path)
                    except: pass
                if attempt < max_retries:
                    await asyncio.sleep(retry_delay)
                    continue
                return None

        return None

    # ---------------- autoplay helpers ----------------

    def _format_duration(self, seconds: int) -> str:
        seconds = max(int(seconds or 0), 0)
        h, rem = divmod(seconds, 3600)
        m, s = divmod(rem, 60)
        if h:
            return f"{h}:{m:02d}:{s:02d}"
        return f"{m}:{s:02d}"

    def _format_views(self, count) -> str:
        if not count:
            return ""
        count = int(count)
        if count >= 1_000_000:
            return f"{count / 1_000_000:.1f}M views"
        if count >= 1_000:
            return f"{count / 1_000:.1f}K views"
        return f"{count} views"

    def _extract_related(self, video_id: str) -> dict | None:
        opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": "in_playlist",
            "skip_download": True,
            "ignoreerrors": True,
            "geo_bypass": True,
            "socket_timeout": 5, # 🚀 SPEED UP: Isko 10 se 5 kar diya taki response jaldi process ho
            "retries": 1,
            "extractor_retries": 1,
            "extractor_args": {"youtube": {"player_client": ["android"]}},
        }
        url = f"https://www.youtube.com/watch?v={video_id}&list=RD{video_id}"
        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(url, download=False)

    async def _related_from_mix(self, video_id: str, played: set[str]):
        from AloneX.helpers import Track
        
        loop = asyncio.get_event_loop()
        try:
            info = await asyncio.wait_for(
                loop.run_in_executor(None, self._extract_related, video_id),
                timeout=15, # 🚀 SPEED UP: Iska wait time kam kar diya hai 
            )
        except asyncio.TimeoutError:
            logger.warning(f"[Autoplay] Mix fetch timed out for {video_id}.")
            return None
        except Exception as e:
            logger.error(f"[Autoplay] Mix fetch failed for {video_id}: {e}")
            return None

        entries = (info or {}).get("entries") or []
        for entry in entries:
            if not entry:
                continue

            eid = entry.get("id")
            if not eid or eid in played:
                continue

            title = entry.get("title") or "Unknown"
            if title.lower() in ("[deleted video]", "[private video]"):
                continue

            duration = int(entry.get("duration") or 0)
            if duration <= 0 or duration > config.DURATION_LIMIT:
                continue

            thumbs = entry.get("thumbnails") or []
            thumbnail = thumbs[-1]["url"].split("?")[0] if thumbs else None

            return Track(
                id=eid,
                channel_name=entry.get("channel") or entry.get("uploader") or "YouTube",
                duration=self._format_duration(duration),
                duration_sec=duration,
                title=title[:25],
                thumbnail=thumbnail,
                url=f"https://www.youtube.com/watch?v={eid}",
                view_count=self._format_views(entry.get("view_count")),
                video=False,
            )

        return None

    async def _related_from_search(self, current, played: set[str]):
        from AloneX.helpers import Track, utils
        
        queries = []
        if current.title and current.channel_name:
            queries.append(f"{current.title} {current.channel_name}")
        if current.channel_name:
            queries.append(f"{current.channel_name} best songs")
        if current.title:
            queries.append(f"{current.title} similar songs")

        for query in queries:
            try:
                # Limit 5 kiya taki loop chota rahe aur jaldi related song mil jaye
                _search = VideosSearch(query, limit=5)
                results = await _search.next()
            except Exception as e:
                logger.error(f"[Autoplay] Search fallback failed for {query!r}: {e}")
                continue

            for data in (results or {}).get("result", []):
                eid = data.get("id")
                if not eid or eid in played:
                    continue

                duration_str = data.get("duration")
                duration_sec = utils.to_seconds(duration_str) if duration_str else 0
                if not duration_sec or duration_sec > config.DURATION_LIMIT:
                    continue

                return Track(
                    id=eid,
                    channel_name=data.get("channel", {}).get("name") or "YouTube",
                    duration=duration_str,
                    duration_sec=duration_sec,
                    title=(data.get("title") or "Unknown")[:25],
                    thumbnail=(data.get("thumbnails", [{}])[-1].get("url") or "").split("?")[0] or None,
                    url=data.get("link"),
                    view_count=data.get("viewCount", {}).get("short"),
                    video=False,
                )

        return None

    async def get_related(self, current, played: list[str] | None = None):
        if not current or not current.id:
            return None

        played = set(played or [])
        played.add(current.id)

        related = await self._related_from_mix(current.id, played)
        if related:
            return related

        logger.info(
            f"[Autoplay] Mix returned nothing for {current.id}, trying search fallback."
        )
        
        related = await self._related_from_search(current, played)
        if related:
            return related

        logger.warning(f"[Autoplay] No related track found for {current.id}.")
        return None
        
