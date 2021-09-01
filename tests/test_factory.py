from hktkzyx_toolbox_web import create_app


def test_create_app():
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing


def test_hello_world(client):
    response = client.get('/hello')
    assert response.data == b'Hello, World!'
