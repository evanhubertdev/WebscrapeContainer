from scrapers import *
#from selenium import webdriver
import unittest

class TestScrapeMethods(unittest.TestCase):

    def test_cars(self):
        teststring = open("Testing/test_cars.txt", 'r')
        expected_json = teststring.read()
        teststring.close()
        self.assertEqual(scrapeCars(), expected_json)
'''
    def test_news(self):
        teststring = open("Testing/test_news.txt", 'r')
        expected_json = teststring.read()
        teststring.close()
        self.assertEqual(scrapeNews(), expected_json)
'''

if __name__ == '__main__':
    unittest.main() 













