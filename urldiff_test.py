#!/usr/bin/env python3

import unittest
from urldiff import url_distance, path_distance, iter_distance, query_distance, is_url_subset


class TestUrlDistance(unittest.TestCase):
    """ Run with `python3 -m unittest urldiff.py` """

    def test_url_distance_equal(self):
        u1 = "http://www.google.com/search?q=term#fragment"
        u2 = "http://www.google.com/search/path/?q=term#fragment"
        self.assertEqual(url_distance(u1, u1), 0)
        self.assertEqual(url_distance(u2, u2), 0)

    def test_url_distance_not_equal(self):
        u1 = "http://www.google.com/search?q=term#fragment"
        u2 = "http://www.google.com/search/path/?q=term#fragment"
        self.assertNotEqual(url_distance(u1, u2), 0)

    def test_path_distance_not_equal(self):
        u1 = "http://www.google.com/search?q=term#fragment"
        u2 = "http://www.google.com/search/path/?q=term#fragment"
        self.assertNotEqual(path_distance(u1, u2), 0)

    def test_path_distance(self):
        u1 = "/"
        u2 = "/one.path"
        u3 = "/one.path/more/"

        self.assertEqual(path_distance(u1, u2), 1)
        self.assertEqual(path_distance(u2, u3), 2)

    def test_url_distance_less(self):
        u1 = "http://www.google.com/search/?q=term#fragment"
        u2 = "http://www.google.com/search/path/?q=term#fragment"
        u3 = "http://www.google.com/search/path/again/?q=term#fragment"
        distance_12 = path_distance(u1, u2)
        distance_13 = path_distance(u1, u3)
        self.assertLess(distance_12, distance_13)

    def test_query_distance_less(self):
        u1 = "http://www.google.com/search?a=term"
        u2 = "http://www.google.com/search/path/?a=term&b=term"
        u3 = "http://www.google.com/search/path/?a=term&b=term&c=term"
        self.assertLess(query_distance(u1, u2), query_distance(u1, u3))

    def test_associative(self):
        u1 = "http://www.google.se:80/search//?a=term"
        u2 = "https://www.google.com/search/one/;p=1?a=term&b=term"
        u3 = "http://user:pass@www.google.com/search/path/b/c/d;param=44;param2=12?a=term&b=term&c=ter&a=1m#hash"

        self.assertEqual(url_distance(u1, u2), url_distance(u2, u1))
        self.assertEqual(url_distance(u2, u3), url_distance(u3, u2))
        self.assertEqual(url_distance(u1, u3), url_distance(u3, u1))

    def test_is_url_subset(self):
        u1 = "/file.php?query=value"
        u2 = "http://webmail.com/file.php?query=value"
        u3 = "http://webmail.com/file.php?query=value&another=value"
        u4 = "http://webmail.com/file.php/something/more?query=value&another=value#hash"

        self.assertFalse(is_url_subset(u1, u2))
        self.assertFalse(is_url_subset(u2, u1))
        self.assertFalse(is_url_subset(u3, u2))

        self.assertTrue(is_url_subset(u2, u3))
        self.assertTrue(is_url_subset(u3, u4))
        self.assertTrue(is_url_subset(u4, u4))

    def test_query_distance_equal(self):
        u1 = "?a=1&b=b&c=3"
        u2 = "?b=b&c=3&a=1"

        self.assertEqual(query_distance(u1, u2), query_distance(u2, u1))

    def test_path_distance_equal(self):
        u1 = "/one/two/three"
        u2 = "/one/two/three/four"
        u3 = "/one/one/three/four"

        self.assertEqual(path_distance(u1, u1), 0)
        self.assertEqual(path_distance(u1, u2), 1)
        self.assertEqual(path_distance(u1, u3), 2)

        u = "http://www.google.com/search?q=term#fragment"
        self.assertEqual(path_distance(u, u), 0)

        u = "http://www.google.com/search/path/?q=term#fragment"
        self.assertEqual(path_distance(u, u), 0)

    def test_query_distance_zero(self):
        q = "?a=1&b=b&c=3"
        self.assertEqual(query_distance(q, q), 0)

    def test_iter_distance_zero(self):
        a1 = [1, 2, 3, 4]
        a2 = (1, 2, 3, 4)
        self.assertEqual(iter_distance(a1, a2), 0)

    def test_iter_distance_less(self):
        a1 = (1, 2, 3, 4)
        a2 = [1, 2, 10, 20]
        a3 = [1, 5, 5, 5]

        small_distance = iter_distance(a1, a2)
        big_distance = iter_distance(a1, a3)
        self.assertLess(small_distance, big_distance)

    def test_iter_distance_extra(self):
        a1 = (1, 2, 3)
        a2 = (1, 2, 3, 4)
        self.assertEqual(iter_distance(a1, a2), 1)

    def test_qs_difference_big(self):
        u1 = "https://sv.wikipedia.org/w/index.php"
        u2 = "https://sv.wikipedia.org/w/index.php?a=1&b=2&c=3&d=4&e=5"
        u3 = "?a=1&b=2&c=3&d=4&e=5&f=6&g=7"

        self.assertEqual(query_distance(u1, u2), 5)
        self.assertEqual(query_distance(u2, u3), 2)

    def test_qs_difference_empty(self):
        u1 = None
        u2 = ""
        u3 = "https://sv.wikipedia.org/w/index.php"
        u4 = "https://sv.wikipedia.org/w/index.php?a=1&b=2&c=3&d=4&e=5"

        self.assertEqual(query_distance(u1, u2), 0)
        self.assertEqual(query_distance(u1, u4), 5)
        self.assertEqual(query_distance(u2, u4), 5)
        self.assertEqual(query_distance(u3, u4), 5)


if __name__ == '__main__':
    unittest.main()
