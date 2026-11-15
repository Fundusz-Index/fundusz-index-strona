import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page()
        await pg.goto("file://" + str(__import__("pathlib").Path(__file__).resolve().parent / "oferta.html") + ""); await pg.wait_for_timeout(500)
        over=await pg.evaluate("[...document.querySelectorAll('.page')].map(e=>e.scrollHeight-e.clientHeight)")
        print("overflow px per page:",over)
        await pg.pdf(path=str(__import__("pathlib").Path(__file__).resolve().parents[2] / "pliki" / "fundusz-index-oferta-wspolpracy.pdf"), format="A4", print_background=True, prefer_css_page_size=True)
        await b.close()
asyncio.run(main())
