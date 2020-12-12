#!/usr/bin/env python3

import argparse
import bs4
import configargparse
import io
import re
import requests
import sys


def get_options():
    p = configargparse.ArgParser(default_config_files=['~/.marklink'])
    p.add('files', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
    p.add('-f', '--format', help='which format', type=str, default='md', choices=['md', 'org', 'html'])
    p.add('-q', '--remove-query', help='remove query parameters', action='store_true', default=False)
    return p.parse_args()


def get_title(url):

    # logging.debug('Getting title for {url}'.format(url))

    if not url.startswith('http'):
        url = 'https://' + url

    r = requests.get(url)

    soup = bs4.BeautifulSoup(r.text, 'lxml')

    return soup.title.text


def remove_query_args(url):

    # Let me know when this isn't good enough
    return url.rsplit('?', maxsplit=1)[0]


def to_md(title, url):

    return '[{title}]({url})'.format(title=title, url=url)


def to_html(title, url):

    return '<a href="{url}">{title}</a>'.format(url=url, title=title)


def to_org(title, url):

    return '[[{url}][{title}]]'.format(title=title, url=url)


def handle_matchobj(matchobj):

    title = matchobj.group('title')
    url = matchobj.group('url')

    if get_options().remove_query:
        url = remove_query_args(url)

    if not title:
        title = get_title(url)
        title = title.strip()

    fmt = get_options().format

    if fmt == 'md':
        return to_md(title, url)
    elif fmt == 'org':
        return to_org(title, url)
    elif fmt == 'html':
        return to_html(title, url)


def main():

    opts = get_options()

    # Make this more readable
    url_pattern = r'(?:\[(?P<title>[^\]]*)\]\(|\b)(?P<url>(?:(?:https?)://|(?:www)\.)[-A-Z0-9+&@/%?=~_|$!:,.;]*[A-Z0-9+&@#/%=~_|$])\)?'
    regex = re.compile(url_pattern, flags=re.IGNORECASE)

    f = io.StringIO(initial_value='')

    for line in opts.files:
        f.write(re.sub(regex, handle_matchobj, line))

    print(f.getvalue(), end='')


if __name__ == '__main__':
    main()
