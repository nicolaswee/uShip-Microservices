from flask import Flask
import json
from cart import app

def test_debug():
    assert not app.debug, 'Ensure the app not in debug mode'

def test_addProduct():
    client = app.test_client()
    url = "/addProduct"

    body = {
        'email': 'test@test.com',
        'uid': 'test'
    }

    response = client.post(url, data=json.dumps(body), content_type='application/json')
    print(response)
    assert response.status_code == 200

def test_removeProduct():
    client = app.test_client()
    url = "/removeProduct"

    body = {
        'email': 'test@test.com',
        'uid': 'test'
    }

    response = client.post(url, data=json.dumps(body), content_type='application/json')
    assert response.status_code == 200