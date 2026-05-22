import aiohttp
import json
import re
from bs4 import BeautifulSoup

async def get_pinterest_media(url: str) -> dict | None:
    """
    Линкро аз Pinterest мегирад ва истиноди мустақими видео ё сураткушоро бармегардонад.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5"
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        try:
            if "pin.it" in url:
                async with session.head(url, allow_redirects=True, timeout=10) as response:
                    url = str(response.url)

            async with session.get(url, timeout=10) as response:
                if response.status != 200:
                    return None
                html = await response.text()

            soup = BeautifulSoup(html, "html.parser")

            video_links = re.findall(r'https://v1\.pinimg\.com/videos/[^"\']+\.mp4', html)
            if video_links:
                return {"type": "video", "url": video_links[0]}

            video_tag = soup.find("meta", property="og:video:secure_url") or soup.find("meta", property="og:video")
            if video_tag and video_tag.get("content"):
                return {"type": "video", "url": video_tag.get("content")}

            image_tag = soup.find("meta", property="og:image")
            if image_tag and image_tag.get("content"):
                if "video" in html or soup.find("video"):
                    html_video = soup.find("video")
                    if html_video and html_video.get("src"):
                        return {"type": "video", "url": html_video.get("src")}
                
                img_url = image_tag.get("content")
                img_url = img_url.replace("/736x/", "/originals/").replace("/ch/", "/originals/")
                return {"type": "image", "url": img_url}

            script_tag = soup.find("script", id="__PWS_DATA__")
            if script_tag:
                data = json.loads(script_tag.string)
                try:
                    am_data = data["props"]["initialRequests"][0]["response"]["data"]["v3GetPinBySlug"]["data"]
                    if "videos" in am_data and am_data["videos"]:
                        video_url = am_data["videos"]["video_list"]["V_720P"]["url"]
                        return {"type": "video", "url": video_url}
                except Exception:
                    pass

        except Exception as e:
            print(f"Хатогӣ ҳангоми парсинг: {e}")
            return None

    return None