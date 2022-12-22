from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    price: int


ITEMDB = {}


@app.get("/items")
async def get_items():
    return ITEMDB


@app.post("/items/{item_id}")
async def update_item(item_id, item: Item):
    global ITEMDB
    ITEMDB[item_id] = item
    return item


client = TestClient(app)


def test_api_flow():
    response = client.get("/items")
    assert response.status_code == 200
    assert response.json() == {}

    response = client.post(
        "/items/1",
        json={"name": "Book", "price": 1980},
    )
    assert response.status_code == 200
    assert response.json() == {'name': 'Book', 'price': 1980}

    response = client.post(
        "/items/2",
        json={"name": "PC", "price": 98000},
    )
    assert response.status_code == 200
    assert response.json() == {'name': 'PC', 'price': 98000}

    response = client.get("/items")
    assert len(response.json()) == 2
    assert response.json() == {
        "1": {'name': 'Book', 'price': 1980},
        "2": {'name': 'PC', 'price': 98000}
    }


