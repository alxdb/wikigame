import pytest

import wikigame.wikiapi


@pytest.mark.asyncio
async def test_request_page():
    async with wikigame.wikiapi.WikiApi() as wikiapi:
        response = [result async for result in wikiapi.request({"titles": "Main Page"})]
        assert len(response) == 1
        page = response[0]["pages"][0]
        assert page["pageid"] == 15580374
        assert page["ns"] == 0
        assert page["title"] == "Main Page"


@pytest.mark.asyncio
async def test_request_non_existent_page():
    async with wikigame.wikiapi.WikiApi() as wikiapi:
        response = [
            result
            async for result in wikiapi.request(
                {"titles": "Garbled nonsense fdoaf2390r23"}
            )
        ]
        assert response[0]["pages"][0]["missing"] is True


@pytest.mark.asyncio
async def test_random_pages():
    async with wikigame.wikiapi.WikiApi() as wikiapi:
        n_pages = 5
        response = [result async for result in wikiapi.random_pages(n_pages)]
        assert len(response) == n_pages


@pytest.mark.asyncio
async def test_links():
    async with wikigame.wikiapi.WikiApi() as wikiapi:
        page = await anext(wikiapi.random_pages(1))
        assert page
        links = [x async for x in wikiapi.links(page)]
        assert links
        links_here = [x async for x in wikiapi.links_here(page)]
        assert links_here
