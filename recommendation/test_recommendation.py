from flask import Flask
from recommendation import app

def test_debug():
    assert not app.debug, 'Ensure the app not in debug mode'