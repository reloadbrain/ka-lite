"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import sys
import random
import requests
import urllib

from django.test import TestCase, LiveServerTestCase
from django.core.management import call_command
from django.test.client import Client

from utils import caching
from kalite.main import topicdata


class SimpleTest(LiveServerTestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

    def test_cache_invalidation(self):

        # Get a random youtube id
        n_videos = len(topicdata.NODE_CACHE['Video'])
        video_slug = topicdata.NODE_CACHE['Video'].keys()[random.randint(0,n_videos-1)]
        youtube_id = topicdata.NODE_CACHE['Video'][video_slug]['youtube_id']
        video_path = "/topics" + topicdata.NODE_CACHE['Video'][video_slug]['path']

        # Clean the cache for this item
        caching.expire_page(path=video_path)
        
        # Create the cache item, and check it
        self.assertTrue(not caching.has_cache_key(path=video_path))
        urllib.urlopen(self.live_server_url + video_path).close()
        self.assertTrue(caching.has_cache_key(path=video_path))

        # Invalidate the cache item, and check it
        #caching.expire_page(path=video_path)
        caching.invalidate_cached_video_page(youtube_id) # test the convenience function
        
        self.assertTrue(not caching.has_cache_key(path=video_path))

    
    def test_cache_across_clients(self):

        # Get a random youtube id
        n_videos = len(topicdata.NODE_CACHE['Video'])
        video_slug = topicdata.NODE_CACHE['Video'].keys()[random.randint(0,n_videos-1)]
        youtube_id = topicdata.NODE_CACHE['Video'][video_slug]['youtube_id']
        video_path = "/topics" + topicdata.NODE_CACHE['Video'][video_slug]['path']

        # Clean the cache for this item
        caching.expire_page(path=video_path)
        self.assertTrue(not caching.has_cache_key(path=video_path), "No cache key after expiring the page")
                
        # Set up the cache with Django client
        Client().get(video_path)
        self.assertTrue(caching.has_cache_key(path=video_path), "Cache key exists after Django Client get")
        caching.expire_page(path=video_path) # clean cache
        self.assertTrue(not caching.has_cache_key(path=video_path), "No cache key after expiring the page")
                
        # Get the same cache key when getting with urllib, and make sure the cache is created again
        urllib.urlopen(self.live_server_url + video_path).close()
        self.assertTrue(caching.has_cache_key(path=video_path), "Cache key exists after urllib get")
        caching.expire_page(path=video_path) # clean cache
        self.assertTrue(not caching.has_cache_key(path=video_path), "No cache key after expiring the page")
        
        # 
        requests.get(self.live_server_url + video_path)
        self.assertTrue(caching.has_cache_key(path=video_path), "Cache key exists after urllib get")
        caching.expire_page(path=video_path) # clean cache
        self.assertTrue(not caching.has_cache_key(path=video_path), "No cache key after expiring the page")

    
    