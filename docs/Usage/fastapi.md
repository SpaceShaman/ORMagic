# Integration with [FastAPI](https://fastapi.tiangolo.com/)

Because ORMagic is based on [Pydantic](https://docs.pydantic.dev), it can be easily integrated with [FastAPI](https://fastapi.tiangolo.com/).
Below is an example of how to use ORMagic with [FastAPI](https://fastapi.tiangolo.com/) to create a simple CRUD REST API.

```python
from fastapi import FastAPI
from ormagic import DBModel

app = FastAPI()

class User(DBModel):
    name: str
    age: int

User.create_table()

@app.post("/users/")
def create_user(user: User):
    return user.save()

@app.get("/users/")
def read_users():
    return User.all()

@app.get("/users/{id}")
def read_user(id: int):
    return User.get(id=id)

@app.put("/users/{id}")
def update_user(id: int, user: User):
    user.id = id
    return user.save()

@app.delete("/users/{id}")
def delete_user(id: int):
    User.get(id=id).delete()
    return {"message": "User deleted"}
```