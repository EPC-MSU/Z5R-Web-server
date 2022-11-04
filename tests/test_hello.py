from unittest import TestCase
from hello_world.app import say_hello
from src.z5r_web import Z5RWebController

class TestHello(TestCase):
    def test_hello_say(self):
        self.assertTrue(say_hello() == "Hello")

class TestZ5RWebController(TestCase):
    def test_creation(self):
        try:
            z5r = Z5RWebController(0)
            z5r.add_card()
            z5r.del_card()
        except Exception:
            self.assertTrue(False)
