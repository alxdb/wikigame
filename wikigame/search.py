import logging
from typing import Iterator, Literal, Self

from ordered_set import OrderedSet

from wikigame.wikiapi import Page, WikiApi

SearchMode = Literal["source"] | Literal["target"]


class Search:
    def __init__(self, page: Page, search_mode: SearchMode):
        self.search_space: dict[Page, list[Page]] = {page: []}
        self.search_queue = OrderedSet([page])
        self.search_mode = search_mode

    async def extend_search(self, wikiapi: WikiApi, other: Self) -> set[Page]:
        search_head = self.search_queue.pop(0)
        logging.info(f"Searching {self.search_mode}: {search_head}")

        links = await self._find_links(search_head, wikiapi)

        # self.search_space |= links
        for link in links:
            self.search_space.setdefault(link, []).append(search_head)

        result = self.search_space.keys() & other.search_space.keys()
        if not result:
            # self.search_queue.extend(links)
            self.search_queue |= OrderedSet(links)
        return result

    async def _find_links(self, page: Page, wikiapi: WikiApi) -> OrderedSet[Page]:
        match self.search_mode:
            case "source":
                search_method = wikiapi.links
            case "target":
                search_method = wikiapi.links_here
            case _:
                raise RuntimeError(f"Invalid search mode: {self.search_mode}")
        return OrderedSet([link async for link in search_method(page)])

    def find_route(self, page: Page) -> Iterator[Page] | None:
        if page not in self.search_space:
            return None

        links = self.search_space[page]
        while len(links) != 0:
            if len(links) > 1:
                logging.warn(f"Ignoring links: {links[1:]}")
            link = links[0]
            yield link
            links = self.search_space[link]


async def find_route(wikiapi: WikiApi, source: Page, target: Page) -> set[Page]:
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
