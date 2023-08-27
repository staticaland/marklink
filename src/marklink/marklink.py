#!/usr/bin/env python3

import functools
import argparse
import bs4
import configargparse
import io
import re
import requests
import sys
from .__version__ import __version__


def remove_prefix(text: str, prefix: str) -> str:
    """
    Remove the specified prefix from the given text.

    Args:
        text (str): The text to remove the prefix from.
        prefix (str): The prefix to remove.

    Returns:
        str: The text with the prefix removed.
    """
    if text.startswith(prefix):
        return text[len(prefix) :]
    return text


def transform_youtube(url: str, title: str) -> str:
    """
    Transform the title of a YouTube URL.

    Args:
        url (str): The YouTube URL.
        title (str): The original title.

    Returns:
        str: The transformed title.
    """
    if "youtube.com" in url:
        oembed_json = requests.get(f"https://www.youtube.com/oembed?format=json&url={url}").json()
        return oembed_json.get("title", title)
    return None


def transform_github(url: str, title: str) -> str:
    """
    Transform the title of a GitHub URL.

    Args:
        url (str): The GitHub URL.
        title (str): The original title.

    Returns:
        str: The transformed title.
    """
    if "github.com" in url:
        return re.sub(r"^GitHub - ", "", title)
    return None


available_transformers = []
available_transformers.append(transform_youtube)
available_transformers.append(transform_github)


def get_options() -> argparse.Namespace:
    """
    Get the command line options.

    Returns:
        argparse.Namespace: The command line options.
    """
    p = configargparse.ArgParser(default_config_files=["~/.marklink"])

    p.add("files", nargs="?", type=argparse.FileType("r"), default=sys.stdin)

    p.add(
        "-f",
        "--format",
        help="which format",
        type=str,
        default="md",
        choices=["md", "org", "html"],
    )

    p.add(
        "-q",
        "--remove-query",
        help="remove query parameters",
        action="store_true",
        default=False,
    )

    p.add(
        "-t",
        "--transformers",
        help="comma separated list of transformers",
        type=str,
        default="github,youtube",
    )

    return p.parse_args()


def get_title(url: str) -> str:
    """
    Get the title of a web page.

    Args:
        url (str): The URL of the web page.

    Returns:
        str: The title of the web page.
    """
    if not url.startswith("http"):
        url = "https://" + url

    session = requests.Session()
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/User-Agent#library_and_net_tool_ua_strings
    session.headers.update({"User-Agent": f"marklink/{__version__}"})
    r = session.get(url)

    soup = bs4.BeautifulSoup(r.text, "lxml")

    title = soup.title.text

    return title


def remove_query_args(url: str) -> str:
    """
    Remove the query parameters from a URL.

    Args:
        url (str): The URL.

    Returns:
        str: The URL without the query parameters.
    """
    return url.rsplit("?", maxsplit=1)[0]


def to_md(title: str, url: str) -> str:
    """
    Convert a title and URL to a Markdown link.

    Args:
        title (str): The title.
        url (str): The URL.

    Returns:
        str: The Markdown link.
    """
    return "[{title}]({url})".format(title=title, url=url)


def to_html(title: str, url: str) -> str:
    """
    Convert a title and URL to an HTML link.

    Args:
        title (str): The title.
        url (str): The URL.

    Returns:
        str: The HTML link.
    """
    return '<a href="{url}">{title}</a>'.format(url=url, title=title)


def to_org(title: str, url: str) -> str:
    """
    Convert a title and URL to an Org link.

    Args:
        title (str): The title.
        url (str): The URL.

    Returns:
        str: The Org link.
    """
    return "[[{url}][{title}]]".format(title=title, url=url)


def handle_matchobj(matchobj: re.Match, transformers: list, fmt: str) -> str:
    """
    Handle a match object and return the formatted link.

    Args:
        matchobj (re.Match): The match object.
        transformers (list): The list of transformers.
        fmt (str): The format of the link.

    Returns:
        str: The formatted link.
    """
    title = matchobj.group("title")
    url = matchobj.group("url")

    if get_options().remove_query:
        url = remove_query_args(url)

    if not title:
        title = get_title(url)
        title = title.strip()

    transformed_title = None

    for transformer in transformers:
        if transformed_title is not None:
            break
        transformed_title = transformer(url, title)

    if transformed_title:
        title = transformed_title

    format_mapper = {
        'md': to_md,
        'org': to_org,
        'html': to_html,
    }

    return format_mapper[fmt](title, url)


def main() -> None:
    """
    The main function.
    """
    opts = get_options()

    wanted_transformers = opts.transformers
    wanted_transformers = wanted_transformers.split(",")

    enabled_transformers = [
        fn
        for fn in available_transformers
        if remove_prefix(fn.__name__, "transform_") in wanted_transformers
    ]

    # Make this more readable
    url_pattern = r"(?:\[(?P<title>[^\]]*)\]\(|\b)(?P<url>(?:(?:https?)://|(?:www)\.)[-A-Z0-9+&@/%?=~_|$!:,.;]*[A-Z0-9+&@#/%=~_|$])\)?"
    regex = re.compile(url_pattern, flags=re.IGNORECASE)

    f = io.StringIO(initial_value="")

    # Since we want to pass transformers and markup format from the CLI, we need
    # a way to feed it into the handle_matchobj function. Here functools.partial
    # comes to the rescue!
    # https://stackoverflow.com/questions/3218283/how-to-pass-a-variable-to-a-re-sub-callback
    for line in opts.files:
        f.write(
            re.sub(
                regex,
                functools.partial(
                    handle_matchobj, transformers=enabled_transformers, fmt=opts.format
                ),
                line,
            )
        )

    print(f.getvalue(), end="")

if __name__ == "__main__":
    main()
