from flask import Flask
from news import app

def test_debug():
    assert not app.debug, 'Ensure the app not in debug mode'

def test_getNews():
    client = app.test_client()
    url = "/getNews?country=idkwhereiam&count=10"

    response = client.get(url)
    assert response.status_code == 401