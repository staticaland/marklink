#!/usr/bin/env python3

import requests
import bs4
import re
import argparse
import configargparse
import sys


def get_options():
    p = configargparse.ArgParser(default_config_files=['/etc/app/conf.d/*.conf', '~/.markylink'])
    p.add('infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
    p.add('-q', help='remove query parameters', action='store_true')
    return p.parse_args()


def get_title(url):
    print('Getting title for:', url)
    if not url.startswith('http'):
        url = 'https://' + url
    r = requests.get(url)
    soup = bs4.BeautifulSoup(r.text, 'lxml')
    return soup.title.text


def remove_query_args(url):
    return url[:url.find('?')]


def url_to_markdown_link(matchobj):
    url = matchobj.group(0)
    return('[{title}]({url})'.format(title=get_title(url), url=url))


def main():

    opts = get_options()

    rere = re.compile(r'\b((https?)://|(www)\.)[-A-Z0-9+&@/%?=~_|$!:,.;]*[A-Z0-9+&@#/%=~_|$]', re.IGNORECASE)

    for line in opts.infile:
        print(re.sub(rere, url_to_markdown_link, line))


if __name__ == '__main__':
    main()
