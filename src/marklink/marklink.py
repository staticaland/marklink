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


def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix) :]
    return text


def transform_youtube(url, title):
    if "youtube.com" in url:
        oembed_json = requests.get(f"https://www.youtube.com/oembed?format=json&url={url}").json()
        return oembed_json.get("title", title)
    return None


def transform_github(url, title):
    if "github.com" in url:
        return re.sub(r"^GitHub - ", "", title)
    return None


available_transformers = []
available_transformers.append(transform_youtube)
available_transformers.append(transform_github)


def get_options():

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
        help="comma seperated list of transformers",
        type=str,
        default="github,youtube",
    )
    return p.parse_args()


def get_title(url):

    if not url.startswith("http"):
        url = "https://" + url

    session = requests.Session()
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/User-Agent#library_and_net_tool_ua_strings
    session.headers.update({"User-Agent": f"marklink/{__version__}"})
    r = session.get(url)

    soup = bs4.BeautifulSoup(r.text, "lxml")

    title = soup.title.text

    return title


def remove_query_args(url):

    # Let me know when this isn't good enough
    return url.rsplit("?", maxsplit=1)[0]


def to_md(title, url):

    return "[{title}]({url})".format(title=title, url=url)


def to_html(title, url):

    return '<a href="{url}">{title}</a>'.format(url=url, title=title)


def to_org(title, url):

    return "[[{url}][{title}]]".format(title=title, url=url)


def handle_matchobj(matchobj, transformers, fmt):

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

    if fmt == "md":
        return to_md(title, url)
    elif fmt == "org":
        return to_org(title, url)
    elif fmt == "html":
        return to_html(title, url)


def main():

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
