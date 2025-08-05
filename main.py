from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, JSONResponse
import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
import os

app = FastAPI()

@app.get("/screenshot")
async def get_screenshot(symbol: str = Query(...), interval: int = Query(5)):
    try:
        url = f"https://www.tradingview.com/chart/?symbol=FX:{symbol.upper()}"
        filename = f"{symbol}_{interval}m.png"

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
            page = await browser.new_page()
            await page.goto(url, timeout=60000)
            await page.wait_for_selector('div[data-name="pane-legend"]', timeout=60000)
            await asyncio.sleep(5)
            await page.screenshot(path=filename, full_page=True)
            await browser.close()

        return FileResponse(path=filename, filename=filename)

    except PlaywrightTimeoutError:
        return JSONResponse(content={"error": "TradingView page took too long to load."}, status_code=504)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
