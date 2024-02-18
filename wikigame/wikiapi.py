import logging
import urllib.parse
from typing import AsyncIterator, NamedTuple

import aiohttp


class Page(NamedTuple):
    pageid: int
    ns: int
    title: str


class WikiApi:
    def __init__(self):
        self.user_agent = "WikiGame (alxdb@pm.me)"

    async def __aenter__(self):
        self.session = await aiohttp.ClientSession().__aenter__()
        return self

    async def __aexit__(self, *args):
        await self.session.__aexit__(*args)

    async def request(self, params: dict[str, str | int]) -> AsyncIterator[dict]:
        assert self.session is not None

        params.setdefault("action", "query")
        params.setdefault("format", "json")
        params.setdefault("formatversion", 2)

        async def make_request():
            logging.debug(f"wikipedia api request: {params}")
            async with self.session.get(
                "https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode(params),
                headers={"User-Agent": self.user_agent},
            ) as response:
                logging.debug(f"wikipedia api response: {response}")

                response.raise_for_status()

                json = await response.json()
                if "error" in json:
                    raise RuntimeError(f"wikipedia api error: {json['error']}")
                if "warnings" in json:
                    logging.warning(f"wikipedia api warnings: {json['warnings']}")
                return json

        response = await make_request()
        while True:
            if "query" in response:
                yield response["query"]

            if "continue" not in response:
                return
            elif response.get("batchcomplete"):
                return
            else:
                params.update(response["continue"])
                response = await make_request()

    async def random_pages(self, n: int, namespace: int = 0) -> AsyncIterator[Page]:
        async for result in self.request(
            {
                "generator": "random",
                "grnlimit": n,
                "grnnamespace": namespace,
                "grnfilterredir": "nonredirects",
            }
        ):
            for page in result["pages"]:
                yield Page(**page)

    async def links(self, page: Page, namespace: int = 0) -> AsyncIterator[Page]:
        async for result in self.request(
            {"generator": "links", "pageids": page.pageid, "gplnamespace": namespace}
        ):
            for link in result["pages"]:
                if "missing" not in link:
                    yield Page(**link)
                else:
                    logging.debug(f"Found missing page: {link}")

    async def links_here(self, page: Page, namespace: int = 0) -> AsyncIterator[Page]:
        async for result in self.request(
            {
                "generator": "linkshere",
                "pageids": page.pageid,
                "glhnamespace": namespace,
                "glhshow": "!redirect",
            }
        ):
            for link in result["pages"]:
                yield Page(**link)
