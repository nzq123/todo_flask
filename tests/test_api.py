def test_get_full_list(client):
    response = client.get("/home")
    test_dict = {
    "docs": [
        {
            "date": "2001-09-11 00:00:00",
            "desc": 'abc',
            "id": 1
        },
    ],
    "total": 1

    }
    assert response.json == test_dict


def test_get_item_by_id(client):
    response = client.get("/home/1")
    test_todo = {
            "date": "2001-09-11 00:00:00",
            "desc": 'abc',
            "id": 1
        }

    assert response.json == test_todo


def test_add_new_item(client):
    response = client.post("/home", json = {"date": "2024-02-10 15:51:11.284988", "desc": "post_test"})
    assert response.status_code == 200


def test_add_new_wrong_item(client):
    response = client.post("/home", json = {"date": "jd", "desc": "test12345"})
    assert response.status_code == 400


def test_put_item(client):
    response = client.put("/home/1", json = {"date": "2024-02-10 15:51:11.284988", "desc": "put_test"})
    assert response.status_code == 200


def test_put_wrong_id(client):
    response = client.put("/home/887686", json = {"date": "2024-02-10 15:51:11.284988", "desc": "put_test"})
    assert response.status_code == 404


def test_put_wrong_item(client):
    response = client.put("/home/1", json = {"date": "jd", "desc": "put_test"})
    assert response.status_code == 400


def test_delete_item(client):
    response = client.delete("/home/1")
    assert response.status_code == 200


def test_delete_wrong_item(client):
    response = client.delete("/home/10")
    assert response.status_code == 404
