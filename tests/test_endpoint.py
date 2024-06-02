# 3rd party library imports
from fastapi.testclient import TestClient

# local imports
from main import app

client = TestClient(app)


def test_payout_endpoint_with_custom_headers():
    headers = {'Authorization': 'Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhZG1pbkB0ZXN0LmNvbSJ9.2rKwigP6hPq-L6ssB7SSdPdd'
                                'f7TXSE_AIYzAhF2LMPo'}
    response = client.get('/payout', headers=headers)

    assert response.status_code == 200
    assert response.json() == {
        "page": None,
        "pageSize": 3,
        "totalPages": 1,
        "totalDocs": 2,
        "results": [
            {
                "Id": "664bc121b88cb2933945278c",
                "testField": "test_value"
            },
            {
                "Id": "664bc142b88cb2933945278d",
                "testField": "test_value2"
            }
        ]}

    response = client.get('/payout?page=1', headers=headers)
    assert response.status_code == 200
    assert response.json() == {
        "page": 1,
        "pageSize": 3,
        "totalPages": 1,
        "totalDocs": 2,
        "results": [
            {
                "Id": "664bc121b88cb2933945278c",
                "testField": "test_value"
            },
            {
                "Id": "664bc142b88cb2933945278d",
                "testField": "test_value2"
            }
        ]}

    headers['Authorization'] = headers['Authorization'][:-1]
    response = client.get('/payout?page=1', headers=headers)
    assert response.status_code == 400
    assert response.json() == {'detail': 'Invalid token'}
