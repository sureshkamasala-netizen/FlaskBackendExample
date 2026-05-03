import asyncio
from playwright.async_api import async_playwright
import sys

async def play_youtube_video(browser, url, video_id):
    context = await browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )
    page = await context.new_page()
        
    try:
        print(f"Instance {video_id}: Opening video...")
        await page.goto(url, wait_until="networkidle", timeout=60000)
        await page.wait_for_selector("video", timeout=10000)
        
        print(f"Instance {video_id}: Starting playback...")
        await page.keyboard.press("k")
        await page.evaluate("document.querySelector('video').play()")

        await asyncio.sleep(60)  # Watch for 60 seconds
        print(f"Instance {video_id}: Finished watch time.")
    except Exception as e:
        print(f"Instance {video_id}: Error: {e}")
    finally:
        await context.close()

async def run_views(video_url, instances):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        tasks = [play_youtube_video(browser, video_url, i) for i in range(instances)]
        await asyncio.gather(*tasks)
        await browser.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python RunViews.py <video_url> <num_views>")
        sys.exit(1)
    
    video_url = sys.argv[1]
    num_views = int(sys.argv[2])
    
    asyncio.run(run_views(video_url, num_views))