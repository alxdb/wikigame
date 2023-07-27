import logging
from typing import AsyncIterator, Literal, NamedTuple, Self

from wikigame.wikiapi import Page, WikiApi

SearchMode = Literal["source"] | Literal["target"]
SearchSpace = dict[Page, Page | None]


class Route(NamedTuple):
    route: list[Page]

    def __str__(self) -> str:
        result = f"Route: {self.route[0].title}"
        for page in self.route[1:]:
            result += f" -> {page.title}"
        return result


class SearchResult(NamedTuple):
    common_links: set[Page]
    source_space: SearchSpace
    target_space: SearchSpace

    def select_common_link(self) -> Page:
        common_link = next(iter(self.common_links))
        if len(self.common_links) > 1:
            ignored_links = self.common_links
            ignored_links.remove(common_link)
            logging.warn(f"Ignoring common links: {ignored_links}")
        return common_link

    def find_route(self) -> Route | None:
        common_link = self.select_common_link()
        route = []
        # sources
        link = common_link
        while (link := self.source_space[link]) is not None:
            route.append(link)
        route.reverse()
        # common
        route.append(common_link)
        # targets
        link = common_link
        while (link := self.target_space[link]) is not None:
            route.append(link)

        return Route(route)


class Search:
    def __init__(self, page: Page, search_mode: SearchMode):
        self.search_space: SearchSpace = {page: None}
        self.search_queue = [page]
        self.search_mode = search_mode

    async def find_common(self, wikiapi: WikiApi, other: Self) -> SearchResult | None:
        logging.info(f"Searching {self.search_mode}s")
        search_head = self.search_queue.pop(0)
        logging.info(f"Searching for common link in '{search_head.title}'")
        links = []
        async for link in self._search(wikiapi, search_head):
            if link in self.search_space:
                logging.debug(f"Already searched '{link.title}'")
                continue
            else:
                self.search_space[link] = search_head
                links.append(link)
        if common_links := self.search_space.keys() & other.search_space.keys():
            return self._results(other, common_links)
        else:
            logging.info("Common link not found")
            self.search_queue.extend(links)
            logging.info(f"Search queue now contains {len(self.search_queue)} pages")

    def _search(self, wikiapi: WikiApi, page: Page) -> AsyncIterator[Page]:
        match self.search_mode:
            case "source":
                return wikiapi.links(page)
            case "target":
                return wikiapi.links_here(page)
            case _:
                raise RuntimeError(f"Invalid search mode: {self.search_mode}")

    def _results(self, other: Self, common_links: set[Page]) -> SearchResult:
        match self.search_mode:
            case "source":
                return SearchResult(
                    common_links,
                    source_space=self.search_space,
                    target_space=other.search_space,
                )
            case "target":
                return SearchResult(
                    common_links,
                    source_space=other.search_space,
                    target_space=self.search_space,
                )
            case _:
                raise RuntimeError(f"Invalid search mode: {self.search_mode}")


async def find_route(wikiapi: WikiApi, source: Page, target: Page) -> Route:
    sources = Search(source, "source")
    targets = Search(target, "target")

    while True:
        if (search_result := await sources.find_common(wikiapi, targets)) is not None:
            break
        if (search_result := await targets.find_common(wikiapi, sources)) is not None:
            break

    # search_result should never be None
    return search_result.find_route()  # type: ignore
