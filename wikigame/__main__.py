import asyncio
import logging

import wikigame.search
import wikigame.wikiapi


async def main():
    async with wikigame.wikiapi.WikiApi() as wikiapi:
        source, target = [page async for page in wikiapi.random_pages(2)]
        print(f"Searching for {target.title} from {source.title}")
        links = await wikigame.search.find_route(wikiapi, source, target)
        for link in links:
            print(f"{link.title} links pages")


logging.basicConfig(level=logging.INFO)
asyncio.run(main())
