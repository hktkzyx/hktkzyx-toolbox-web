def test_electronics(client):
    assert client.get('/electronics/').status_code == 200
    response = client.post('/electronics/',
                           data={
                               'voltage': 3.3, 'current': 1
                           })
    assert response.status_code == 200
