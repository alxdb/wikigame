import logging
from typing import Literal, Self

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
        logging.debug(f"Searching {self.search_mode}: {search_head}")

        links = await self._find_links(search_head, wikiapi)
        links = [link for link in links if link not in self.search_space]

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

    def find_route(self, page: Page) -> list[Page] | None:
        if page not in self.search_space:
            return None

        route = []
        links = self.search_space[page]
        while len(links) != 0:
            if len(links) > 1:
                logging.warn(f"Ignoring links: {links[1:]}")
            link = links[0]
            route.append(link)
            links = self.search_space[link]
        return route


async def find_route(wikiapi: WikiApi, source: Page, target: Page) -> list[Page]:
    sources = Search(source, "source")
    targets = Search(target, "target")

    common_links = set()
    found_link = False
    while not found_link:
        if common_links := await sources.extend_search(wikiapi, targets):
            break
        if common_links := await targets.extend_search(wikiapi, sources):
            break

    common_link = next(iter(common_links))
    if len(common_links) > 1:
        common_links.remove(common_link)
        logging.warn(f"Ignoring common links: {common_links}")

    source_route = sources.find_route(common_link)
    target_route = targets.find_route(common_link)
    if source_route is None or target_route is None:
        raise RuntimeError("Could not find route for common link")

    route = list(reversed(source_route))
    route.append(common_link)
    route.extend(target_route)
    return route
