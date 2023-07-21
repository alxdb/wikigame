### WikiGame

This python cli application will play the wikipedia game for you.

## The Wiki Game

The [Wiki Game](https://en.wikipedia.org/wiki/Wikipedia:Wiki_Game) consists of selecting two random pages, and attempting to get from one to the other by following the links between them.
Usually, only main article links are allowed (i.e. not help, talk or category pages).

# Six Degrees of Separation

The solution implemented here is inspired by the old addage that there are only six degrees of separation between any two people.
That is to say, if you take two random people and look at their friends, and their friends friends, and their friends friends friends, and so on; 
You will eventually find a friends that the two original people have in common, connected by their friends friends.

The only difference between that idea and the wikipedia game, is that we replace the idea of friends with wikipedia pages (And who doesn't want that).

## Development

This project is managed by [poetry](https://python-poetry.org) and uses black/isort for formatting.
