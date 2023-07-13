import wikipediaapi as wapi
import requests


WAPI = wapi.Wikipedia("WikiGame (alxdb@pm.me)", "en")


def get_random_page() -> wapi.WikipediaPage:
    response = requests.get("https://en.wikipedia.org/api/rest_v1/page/random/title")
    assert response.status_code == 200
    title = response.json()["items"][0]["title"]
    page = WAPI.page(title)
    assert page.exists()
    return page


def found_page() -> None:
    print("Found link!")


def main() -> None:
    # src = WAPI.page("Python_(programming_language)")
    src = get_random_page()
    assert src.exists()
    # dst = WAPI.page("MiNT")
    dst = get_random_page()
    assert dst.exists()
    print(f"{src.title} -> {dst.title}")

    if dst.title in src.links:
        found_page()
        return

    # Breadth first search
    to_search: list[list[wapi.WikipediaPage]] = list()
    searched: set[wapi.WikipediaPage] = set()

    to_search.append([src])
    found_dst = False
    while not found_dst:
        path = to_search.pop(0)
        page = path[-1]
        print(f"Searching: {[page.title for page in path]}")
        if dst.title in page.links:
            found_dst = True
        else:
            print(f"Not found in: {page.title}")
            for link in filter(lambda link: link not in searched, page.links.values()):
                to_search.append(path + [link])

    found_page()


if __name__ == "__main__":
    main()
