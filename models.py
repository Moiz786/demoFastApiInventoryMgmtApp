from datetime import date, datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, Boolean, Float, Date
from pydantic import BaseModel
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class AuthUser(BaseModel):
    """
    A Pydantic model representing the fields required for user authentication.
    """
    name: str
    email: str
    password: Optional[str]


class CreateUser(AuthUser):
    """
    A subclass of AuthUser that includes password validation.
    """
    pass


class TokenSchema(BaseModel):
    """
    A Pydantic model representing an access token and refresh token
    """
    access_token: str
    refresh_token: str


class UserTable(Base):
    """
    An SQLAlchemy model representing the "users" table in the database.
    """
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, nullable=False)


class ItemBase(BaseModel):
    """
    A Pydantic model representing the shared fields of items in the inventory.
    """
    name: Optional[str]
    description: Optional[str]
    price: Optional[float]
    quantity: Optional[int]
    date: Optional[date]
    status: Optional[str]
    sold_units: Optional[int]
    cost: Optional[float]


class ItemCreate(ItemBase):
    """
    A subclass of ItemBase that is used for creating new items.
    """
    pass


class ItemUpdate(ItemBase):
    """
    A subclass of ItemBase that includes the item ID for updating existing items.
    """
    id: int


class ItemDB(ItemBase):
    """
    An SQLAlchemy model representing the "items" table in the database.
    """
    id: int

    class Config:
        orm_mode = True


class Items(Base):
    """
    Attributes:
        -----------
        id : int
            The id of the item. Primary key of the table.
        name : str
            The name of the item.
        description : str
            The description of the item.
        price : float
            The price of the item.
        quantity : int
            The quantity of the item available.
        date : date
            The date the item was added.
        status : str
            The status of the item (Available/Out of Stock).
        sold_units : int
            The number of units of the item sold.
        cost : float
            The cost of the item.
    """
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    date = Column(Date, nullable=False)
    status = Column(String, nullable=False, default="Available")
    sold_units = Column(Integer, default=0)
    cost = Column(Float, nullable=False, default=0)


class TokenPayload(BaseModel):
    """
    A Pydantic model representing the payload of a JWT access token.
    """
    username: str
    exp: datetime
    scopes: Optional[str] = None
    sub: Optional[str]
