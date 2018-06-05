#!/usr/bin/env python3

"""Tests for Marklink."""
import os
import unittest
import re

from marklink import marklink

class MarklinkTestCase(unittest.TestCase):


    def test_main(self):
        stdin = 'some file www.youtube.com object perhaps https://www.youtube.com'
        pass

    def test_to_markdown(self):
        expected_output = '[Stack Overflow](https://stackoverflow.com/)'
        actual_output = marklink.to_markdown(title='Stack Overflow', url='https://stackoverflow.com/')
        self.assertEqual(actual_output, expected_output)

    def test_remove_query_args(self):
        expected_output = 'https://stackoverflow.com/questions'
        actual_output = marklink.remove_query_args('https://stackoverflow.com/questions?sort=votes')
        self.assertEqual(actual_output, expected_output)


if __name__ == '__main__':
    unittest.main()
