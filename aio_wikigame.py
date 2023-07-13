import asyncio
import dataclasses
import logging
import urllib.parse

import aiohttp


@dataclasses.dataclass
class Page:
    id: int
    title: str


class WApi:
    def __init__(self, session: aiohttp.ClientSession):
        self._session = session

    async def _request(self, params: dict[str, str | int]):
        params.setdefault("format", "json")
        params.setdefault("formatversion", "2")
        async with self._session.get(
            "https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode(params),
            headers={"User-Agent": "WikiGame (alxdb@pm.me)"},
        ) as resp:
            return await resp.json()

    async def random_page(self, limit: int = 1) -> list[Page]:
        result = await self._request(
            {
                "action": "query",
                "list": "random",
                "rnnamespace": 0,
                "rnlimit": limit,
            }
        )
        return [Page(page["id"], page["title"]) for page in result["query"]["random"]]

    async def lookup_page(self, title: str) -> Page | None:
        result = await self._request(
            {
                "action": "query",
                "titles": title,
            }
        )
        page = result["query"]["pages"][0]
        return Page(page["pageid"], page["title"])


async def main():
    async with aiohttp.ClientSession() as session:
        wapi = WApi(session)
        page = await wapi.lookup_page("Main Page")
        print(page)


if __name__ == "__main__":
    asyncio.run(main())
