from fastapi.security import OAuth2PasswordRequestForm

import requests
from fastapi.encoders import jsonable_encoder


from db_init import SessionLocal
from models import Items

base_url = "http://127.0.0.1:8000/"
ids = []
headers = {"Content-Type": "application/json"}


def test_add_items():
    item = {
        "name": "test_item_1",
        "description": "this is a test description",
        "price": 2,
        "quantity": 10,
        "date": "2023-04-28",
        "status": "available",
        "sold_units": 2,
        "cost": 5
    }
    response = requests.post(base_url + "items/", json=item, headers=headers)
    item = {**item, "name": "test_item_2", "description": "this is the second new item added for test"}
    response = requests.post(base_url + "items/", json=item, headers=headers)
    assert response.status_code == 200
    assert response.json()['message'] == "Item Added to Inventory System successfully"


def test_get_all_items():
    response = requests.get(base_url + "items/")
    assert response.status_code == 200
    assert response.json()['data'].__len__() >= 2
    assert response.json()['message'] == "All Items"


def test_get_one_item_by_name():
    response = requests.get(
        base_url + "item/?search_term={search_name}&limit=100&options=name".format(search_name='test_item_1'))
    assert response.status_code == 200
    assert response.json()['data'].__len__() == 1
    assert response.json()['message'] == "Items Found"


def test_get_one_item_by_description():
    response = requests.get(
        base_url + "item/?search_term={search_name}&limit=100&options=description".format(
            search_name='this is the second new item added for test'))
    assert response.status_code == 200
    assert response.json()['data'].__len__() == 1
    assert response.json()['message'] == "Items Found"


def test_get_one_item_by_price_lt():
    response = requests.get(
        base_url + "item/?search_term={search_name}&limit=100&options=<".format(
            search_name='2.1'))
    assert response.status_code == 200
    assert response.json()['data'].__len__() >= 1
    assert response.json()['message'] == "Items Found"


def test_get_one_item_by_price_gt():
    response = requests.get(
        base_url + "item/?search_term={search_name}&limit=100&options=>".format(
            search_name='0'))
    assert response.status_code == 200
    assert response.json()['data'].__len__() >= 1
    assert response.json()['message'] == "Items Found"


def test_get_one_item_by_price_eq():
    response = requests.get(
        base_url + "item/?search_term={search_name}&limit=100&options==".format(
            search_name='2'))
    assert response.status_code == 200
    assert response.json()['data'].__len__() >= 1
    assert response.json()['message'] == "Items Found"


def test_get_one_item_by_price_le():
    response = requests.get(
        base_url + "item/?search_term={search_name}&limit=100&options=<=".format(
            search_name='2.1'))
    assert response.status_code == 200
    assert response.json()['data'].__len__() >= 1
    assert response.json()['message'] == "Items Found"


def test_get_one_item_by_price_ge():
    response = requests.get(
        base_url + "item/?search_term={search_name}&limit=100&options=>=".format(
            search_name='2.1'))
    assert response.status_code == 200
    assert response.json()['data'].__len__() >= 1
    assert response.json()['message'] == "Items Found"


def test_update_item():
    with SessionLocal() as db:
        item = db.query(Items.id).filter(Items.name.like('%test_item_%')).first()
        item = {**item, "description": "some random description"}
        response = requests.put(base_url + "items/?item_id={item_id}".format(item_id=id), headers=headers, json=item)
        assert response.status_code == 200
        assert response.json()['message'] == "Item Updated"


def test_delete_new_items():
    with SessionLocal() as db:
        ids = [u.id for u in db.query(Items.id).filter(Items.name.like('%test_item_%')).all()]
        for id in ids:
            response = requests.delete(base_url + "items/?item_id={item_id}".format(item_id=id), headers=headers)
            assert response.status_code == 200
            assert response.json()['message'] == "Item Removed"


def test_sell_item():
    with SessionLocal() as db:
        data = {"username": "waleed", "password": "1234"}
        resp = requests.post(base_url + "login", headers=headers, json=data)
        item = db.query(Items).filter(Items.name.like('%juice%')).first()
        response = requests.put(base_url + "sell/?item_name={item_name}&quantity=1".format(item_name=item.name), headers=headers, json=jsonable_encoder(item))
        assert response.status_code == 200
        assert response.json()['message'] == "Item Updated"
