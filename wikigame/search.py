import logging
from typing import Literal

from wikigame.wikiapi import Page, WikiApi

SearchMode = Literal["source"] | Literal["target"]


class Search:
    def __init__(self, page: Page, search_mode: SearchMode):
        self.search_space = {page}
        self.search_queue = [page]
        self.search_mode = search_mode

    async def extend_search(self, wikiapi: WikiApi, other: "Search") -> set[Page]:
        links = await self._find_links(wikiapi)
        self.search_space |= links
        result = self.search_space & other.search_space
        if not result:
            self.search_queue.extend(links)
        return result

    async def _find_links(self, wikiapi: WikiApi) -> set[Page]:
        search_head = self.search_queue.pop(0)
        logging.info(f"Searching {search_head}")

        match self.search_mode:
            case "source":
                search_method = wikiapi.links
            case "target":
                search_method = wikiapi.links_here
            case _:
                raise RuntimeError("Invalid mode")

        return {page async for page in search_method(search_head)}


async def find_link(wikiapi: WikiApi, source: Page, target: Page) -> set[Page]:
    sources = Search(source, "source")
    targets = Search(target, "target")

    result = set()
    found_link = False
    while not found_link:
        if result := await sources.extend_search(wikiapi, targets):
            break
        if result := await targets.extend_search(wikiapi, sources):
            break
    return result
