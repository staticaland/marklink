#!/usr/bin/env python3

import os

import pytest
import vcr

import marklink

dirname = os.path.dirname(__file__)
cassettedir = os.path.join(dirname, 'cassettes')


@vcr.use_cassette(cassette_library_dir=cassettedir, decode_compressed_response=True)
def test_get_title():
    title = marklink.get_title("https://example.com")
    assert title == "Example Domain"
