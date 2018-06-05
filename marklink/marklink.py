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
    p.add('-q', '--remove-query', help='remove query parameters', action='store_true', default=False)
    p.add('-r', '--replace-url', help='replace plain URLs with markdown links', action='store_true', default=True)
    p.add('-l', '--create-list', help='create a markdown list from all URLs', action='store_true', default=False)
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


def to_markdown(title, url):

    return('[{title}]({url})'.format(title=title, url=url))


def handle_matchobj(matchobj):

    title = matchobj.group('title')
    url = matchobj.group('url')

    if get_options().remove_query:
        url = remove_query_args(url)

    if not title:
        title = get_title(url)

    return to_markdown(title, url)


def main():

    opts = get_options()

    url_pattern = r'(?:\[(?P<title>[^\]]*)\]\(|\b)(?P<url>(?:(?:https?)://|(?:www)\.)[-A-Z0-9+&@/%?=~_|$!:,.;]*[A-Z0-9+&@#/%=~_|$])\)?'
    regex = re.compile(url_pattern, flags=re.IGNORECASE)

    if opts.create_list:

        matches = [m.groupdict() for m in re.finditer(url_pattern, ''.join(opts.files), flags=re.IGNORECASE)]

        for match in matches:
            url = match.get('url')
            title = match.get('title') or get_title(url)
            print('*', to_markdown(title, url))

    if opts.replace_url:

        # http://effbot.org/librarybook/stringio.htm pretty cool, right?
        f = io.StringIO('')

        for line in opts.files:
            f.write(re.sub(regex, handle_matchobj, line))

        print(f.getvalue(), end='')

        f.close()


if __name__ == '__main__':
    main()
