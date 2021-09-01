def test_index(client):
    response = client.get('/')
    assert b'Table of contents' in response.data
    response = client.get('/index')
    assert b'Table of contents' in response.data