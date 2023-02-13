def test_get_full_list(client):
    response = client.get("/home")
    test_dict = {
    "docs": [
        {
            "date": "2023-02-11 18:03:56.028704",
            "desc": "powinno dzialac za 1szym",
            "id": 2
        },
        {
            "date": "2023-02-10 15:51:11.284988",
            "desc": "musi teraz przejsc",
            "id": 3
        },
        {
            "date": "2024-02-10 15:51:11.284988",
            "desc": "test do testow",
            "id": 4
        },
        {
            "date": "2024-02-10 15:51:11.284988",
            "desc": "test12345",
            "id": 5
        },
        {
            "date": "2024-02-10 15:51:11.284988",
            "desc": "test12345",
            "id": 6
        }
    ],
    "total": 5
}

    assert test_dict == response.json


def test_get_item_by_id(client):
    response = client.get("/home/7")
    test_todo = {
            "date": "Sat, 10 Feb 2024 15:51:11 GMT",
            "desc": "put_test",
            "id": 7
    }
    assert test_todo == response.json


def test_add_new_item(client):
    response = client.post("/home", json = {"date": "2024-02-10 15:51:11.284988", "desc": "post_test"})
    assert response.status_code == 200


def test_add_new_wrong_item(client):
    response = client.post("/home", json = {"date": "jd", "desc": "test12345"})
    assert response.status_code == 400


def test_put_item(client):
    response = client.put("/home/7", json = {"date": "2024-02-10 15:51:11.284988", "desc": "put_test"})
    assert response.status_code == 200


def test_put_wrong_id(client):
    response = client.put("/home/887686", json = {"date": "2024-02-10 15:51:11.284988", "desc": "put_test"})
    assert response.status_code == 404


def test_put_wrong_item(client):
    response = client.put("/home/7", json = {"date": "jd", "desc": "put_test"})
    assert response.status_code == 400


def test_delete_item(client):
    response = client.delete("/home/7")
    assert response.status_code == 200


def test_delete_wrong_item(client):
    response = client.delete("/home/7")
    assert response.status_code == 404


#TODO ogarnac ta baze danych druga do testow i testy pozmieniac\