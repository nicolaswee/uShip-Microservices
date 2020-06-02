from flask import Flask
from weather import app

def test_debug():
    assert not app.debug, 'Ensure the app not in debug mode'