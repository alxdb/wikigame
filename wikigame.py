import asyncio
import dataclasses
import logging
import urllib.parse
from typing import AsyncIterator

import aiohttp


@dataclasses.dataclass(frozen=True, eq=True)
class Page:
    title: str


class WApi:
    def __init__(self, session: aiohttp.ClientSession):
        self._session = session

    async def _request(self, params: dict[str, str | int]) -> dict:
        params.setdefault("action", "query")
        params.setdefault("format", "json")
        params.setdefault("formatversion", "2")
        async with self._session.get(
            "https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode(params),
            headers={"User-Agent": "WikiGame (alxdb@pm.me)"},
        ) as response:
            logging.debug(response)
            return await response.json()

    async def request(self, params: dict) -> AsyncIterator[dict]:
        response = await self._request(params)
        logging.debug(response)

        if "error" in response:
            raise RuntimeError(f"API Error: {response['error']}")

        if "warnings" in response:
            logging.warn(f"API Warnings: {response['warnings']}")

        while True:
            yield response["query"]

            if "batchcomplete" in response:
                break

            params.update(response["continue"])
            response = await self._request(params)

    async def random_page(self, limit: int = 1) -> AsyncIterator[Page]:
        async for response in self.request(
            {
                "list": "random",
                "rnnamespace": 0,
                "rnlimit": limit,
            }
        ):
            for page in response["random"]:
                yield Page(page["title"])

    async def lookup_page(self, title: str) -> Page:
        result = await anext(
            self.request(
                {
                    "titles": title,
                }
            )
        )
        return Page(result["pages"][0]["title"])

    async def page_links(self, page: Page) -> AsyncIterator[Page]:
        async for response in self.request(
            {
                "prop": "links",
                "titles": page.title,
                "plnamespace": 0,
                "pllimit": "max",
            }
        ):
            result = response["pages"][0].get("links")
            if result is not None:
                for link in result:
                    yield Page(link["title"])

    async def links_here(self, page: Page) -> AsyncIterator[Page]:
        async for response in self.request(
            {
                "prop": "linkshere",
                "titles": page.title,
                "lhnamespace": 0,
                "lhlimit": "max",
            }
        ):
            result = response["pages"][0].get("linkshere")
            if result is not None:
                for link in result:
                    yield Page(link["title"])


async def main():
    async with aiohttp.ClientSession() as session:
        wapi = WApi(session)
        src, tgt = [page async for page in wapi.random_page(2)]
        logging.info(f"{src=} -> {tgt=}")

        targets = {tgt}
        target_queue = [tgt]

        sources = {src}
        source_queue = [src]

        found_link = False
        while not found_link:
            current_source = source_queue.pop(0)
            source_links = [i async for i in wapi.page_links(current_source)]
            sources |= set(source_links)
            logging.info(f"sources: {len(sources)=} {len(targets)=}")

            if link := sources & targets:
                found_link = True
                logging.info(f"{link=}")
                break
            else:
                source_queue.extend(source_links)

            current_target = target_queue.pop(0)
            target_links = [i async for i in wapi.links_here(current_target)]
            targets |= set(target_links)
            logging.info(f"targets: {len(sources)=} {len(targets)=}")

            if link := sources & targets:
                found_link = True
                logging.info(f"Found {link=}")
                break
            else:
                target_queue.extend(target_links)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    asyncio.run(main())
