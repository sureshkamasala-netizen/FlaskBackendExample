import asyncio
import random
from playwright.async_api import async_playwright
import sys

async def play_youtube_video(browser, url, video_id):
    context = await browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        viewport={"width": 1920, "height": 1080}
    )
    page = await context.new_page()
    await page.set_extra_http_headers({
        "accept-language": "en-US,en;q=0.9",
        "referer": "https://www.youtube.com/"
    })
    await page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {get: () => false});
        Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
        Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
        window.navigator.chrome = { runtime: {} };
    """)

    try:
        print(f"Instance {video_id}: Opening video...")
        await asyncio.sleep(random.uniform(2, 5))
        response = await page.goto(url, wait_until="networkidle", timeout=60000)
        print(f"Instance {video_id}: Page loaded with status {response.status}")
        
        # Check if we got a valid response
        if response.status == 429:
            raise Exception("HTTP 429 Too Many Requests - YouTube is rate limiting this session")
        if response.status != 200:
            raise Exception(f"HTTP {response.status} - Video may be private or unavailable")
        
        # Wait for YouTube player to load
        try:
            await page.wait_for_selector("video", timeout=15000)
            print(f"Instance {video_id}: Video element found")
        except:
            print(f"Instance {video_id}: Video element not found, checking page content...")
            content = await page.content()
            if "Video unavailable" in content or "This video is private" in content:
                raise Exception("Video is private or unavailable")
            await page.wait_for_selector("#movie_player", timeout=15000)
            print(f"Instance {video_id}: Movie player found")
        
        print(f"Instance {video_id}: Starting playback...")
        await page.keyboard.press("k")
        
        # Verify video is playing
        is_playing = await page.evaluate("""
            () => {
                const video = document.querySelector('video');
                return video && !video.paused && video.currentTime > 0;
            }
        """)
        
        if not is_playing:
            print(f"Instance {video_id}: Video not playing, trying direct play...")
            await page.evaluate("document.querySelector('video').play()")
        
        await asyncio.sleep(10)  # Watch for 10 seconds first
        print(f"Instance {video_id}: Watched for 10 seconds, continuing...")
        await asyncio.sleep(50)  # Watch remaining time
        print(f"Instance {video_id}: Finished watch time.")
    except Exception as e:
        print(f"Instance {video_id}: Error: {e}")
    finally:
        await context.close()

async def run_views(video_url, instances):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"],
            ignore_default_args=["--enable-automation"]
        )
        tasks = [play_youtube_video(browser, video_url, i) for i in range(instances)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for idx, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"Instance {idx}: task failed with: {result}")
        await browser.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python RunViews.py <video_url> <num_views>")
        sys.exit(1)
    
    video_url = sys.argv[1]
    num_views = int(sys.argv[2])
    
    asyncio.run(run_views(video_url, num_views))