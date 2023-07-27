import asyncio
import logging

import wikigame.search
import wikigame.wikiapi


async def main():
    async with wikigame.wikiapi.WikiApi() as wikiapi:
        source, target = [page async for page in wikiapi.random_pages(2)]
        print(f"Searching for {target.title} from {source.title}")
        route = await wikigame.search.find_route(wikiapi, source, target)
        print(route)


logging.basicConfig(level=logging.WARN)
asyncio.run(main())
