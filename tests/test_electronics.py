def test_electronics(client):
    assert client.get('/electronics/').status_code == 200