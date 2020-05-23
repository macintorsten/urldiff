#!/usr/bin/env python3

import unittest
from urldiff import url_distance, path_distance, iter_distance, qs_distance
from urllib.parse import urlparse

class TestUrlDistance(unittest.TestCase):
    """ Run with `python3 -m unittest urldiff.py` """

    def test_url_distance_equal(self):
        u1 = urlparse("http://www.google.com/search?q=term#fragment")
        u2 = urlparse("http://www.google.com/search/path/?q=term#fragment")
        self.assertEqual(url_distance(u1, u1), 0)
        self.assertEqual(url_distance(u2, u2), 0)

    def test_url_distance_not_equal(self):
        u1 = urlparse("http://www.google.com/search?q=term#fragment")
        u2 = urlparse("http://www.google.com/search/path/?q=term#fragment")
        self.assertNotEqual(url_distance(u1, u2), 0)

    def test_path_distance_equal(self):
        u = urlparse("http://www.google.com/search?q=term#fragment")
        distance_zero = path_distance(u.path, u.path)
        self.assertEqual(distance_zero, 0)

        u = urlparse("http://www.google.com/search/path/?q=term#fragment")
        distance_zero = path_distance(u.path, u.path)
        self.assertEqual(distance_zero, 0)

    def test_path_distance_not_equal(self):
        u1 = urlparse("http://www.google.com/search?q=term#fragment")
        u2 = urlparse("http://www.google.com/search/path/?q=term#fragment")
        self.assertNotEqual(path_distance(u1.path, u2.path), 0)

    def test_url_distance_less(self):
        u1 = urlparse("http://www.google.com/search?q=term#fragment")
        u2 = urlparse("http://www.google.com/search/path/?q=term#fragment")
        u3 = urlparse("http://www.google.com/search/path/again?q=term#fragment")
        distance_12 = path_distance(u1.path, u2.path)
        distance_13 = path_distance(u1.path, u3.path)
        self.assertLess(distance_12, distance_13)

    def test_qs_distance_equal(self):
        q1 = urlparse("?a=1&b=b&c=3").query
        q2 = urlparse("?b=b&c=3&a=1").query

        d1 = qs_distance(q1, q2)
        d2 = qs_distance(q2, q1)

        self.assertEqual(d1, d2)

    def test_qs_distance_zero(self):
        q = urlparse("?a=1&b=b&c=3").query
        d = qs_distance(q, q)
        self.assertEqual(d, 0)

    def test_iter_distance_zero(self):
        a1 = [1,2,3,4]
        a2 = (1,2,3,4)
        self.assertEqual(iter_distance(a1, a2), 0)

    def test_iter_distance_less(self):
        a1 = (1,2,3,4)
        a2 = [1,2,10,20]
        a3 = [1,5,5,5]

        small_distance = iter_distance(a1, a2)
        big_distance = iter_distance(a1, a3)
        self.assertLess(small_distance, big_distance)
    
    def test_iter_distance_extra(self):
        a1 = (1,2,3)
        a2 = (1,2,3,4)
        self.assertEqual(iter_distance(a1,a2), 1)


if __name__ == '__main__':
    unittest.main()