from datetime import date
from typing import Optional, Union

from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import or_

from fastapi import FastAPI, status, HTTPException, Depends, Query
from fastapi.security import OAuth2PasswordRequestForm
from starlette.responses import JSONResponse

from models import ItemCreate, Items, AuthUser, UserTable, TokenSchema, ItemUpdate
from db_init import SessionLocal
from authentication import refresh_token, create_token, get_current_user, get_hashed_password
from fastapi.encoders import jsonable_encoder
from helpers import profit_for_each_item

sims_app = FastAPI()

# Configure CORS
origins = [
    "http://localhost",
    "http://localhost:3000",
]

sims_app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ops = {
    "<": "__lt__",
    "<=": "__le__",
    "=": "__eq__",
    ">": "__gt__",
    ">=": "__ge__",
    "=>": "__ge__",
    "=<": "__le__"
}


# API Endpoints
@sims_app.post("/items/", summary="Add new item")
def create_item(item: ItemCreate):
    """
        Add a new item to the inventory system.
        Args:
            item: An instance of the `ItemCreate` model, representing the data for the new item to add.
        Returns:
            A JSON response containing a success message and the newly added item data.
        Raises:
            HTTPException: If there is an error adding the item to the database.
        """
    with SessionLocal() as db:
        items_db = Items(**item.dict())
        db.add(items_db)
        db.commit()
        db.refresh(items_db)
        return JSONResponse(content={"message": "Item Added to Inventory System successfully"},
                            status_code=status.HTTP_200_OK)


@sims_app.get("/items/", summary="get all items")
def read_items(skip: int = 0, limit: int = 100):
    """
        Retrieve all items from the inventory.
        Parameters:
        - skip (int): number of items to skip before returning results (default: 0)
        - limit (int): maximum number of items to retrieve (default: 100)
        Returns:
        - JSONResponse: a response containing a list of all items in the inventory, along with a success message
        Raises:
        - HTTPException 404: if there are no items in the inventory
        """
    with SessionLocal() as db:
        items = db.query(Items).offset(skip).limit(limit).all()
        if not items:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inventory is empty...have you tried adding some items"
            )
        return JSONResponse(content={"message": "All Items", "data": jsonable_encoder(items)},
                            status_code=status.HTTP_200_OK)


@sims_app.get("/item/",
              summary="get item(s) by name. For filtering on price use <, = or > signs in options and price in search_term.")
def read_item(search_term: Optional[Union[str, int, None]] = Query(None), limit: int = 100, options: str = Query(None)):
    """
    Get item(s) by name or filter on price using <, =, or > signs in options and price in search_term.
    Parameters:
    - search_term (Optional[Union[str, int, None]]): The name, description, or price of the item to search for. Defaults to None.
    - limit (int): The maximum number of items to return. Defaults to 100.
    - options (str): The search criteria for the `search_term`. Can be "name", "description", or "<", "=", ">". Defaults to None.
    Returns:
    - A JSONResponse object containing the message "Items Found" and a list of item dictionaries.
    Raises:
    - HTTPException(status_code=status.HTTP_404_NOT_FOUND): If no items match the search criteria.
    - HTTPException(status_code=status.HTTP_404_NOT_FOUND): If invalid values are provided for the price or options parameters.
    """
    with SessionLocal() as db:
        is_valid_float = lambda search_term: True if search_term.replace('.', '', 1).isdigit() else False
        price = is_valid_float(search_term)
        if options in ['<', '=', '>'] and not is_valid_float(search_term):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid values for Price. please read the description for details."
            )
        if search_term is None:
            return read_items()
        if options == 'name':
            item = db.query(Items).filter(Items.name.ilike(f"%{search_term}%")).limit(limit).all()
        elif options == 'description':
            item = db.query(Items).filter(Items.description.ilike(f"%{search_term}%")).limit(limit).all()
        elif price:
            if options in ops:
                item = db.query(Items).filter(getattr(Items.price, ops[options])(search_term)).limit(limit).all()
        else:
            item = db.query(Items).filter(
                or_(Items.name.ilike(f"%{search_term}%"), Items.description.ilike(f"%{search_term}%"))).limit(
                limit).all()
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Yikes missing items with your search keywords...try other items"
            )
        return JSONResponse(content={"message": "Items Found", "data": jsonable_encoder(item)},
                            status_code=status.HTTP_200_OK)


@sims_app.put("/items/", summary="update existing item")
def update_item(item: ItemUpdate):
    """
        Endpoint to update an existing item.
        Parameters:
        item (ItemUpdate): The updated item data.
        Returns:
        A JSON response with a message indicating success or failure and the updated item data.
        Raises:
        HTTPException: If no item with the given ID is found.
        """
    with SessionLocal() as db:
        item_db = db.query(Items).filter(Items.id == item.id).first()
        new_data = item.dict(exclude_unset=True)
        if not item_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Queried Item Not Found"
            )
        for key, value in new_data.items():
            setattr(item_db, key, value)
        db.commit()
        db.refresh(item_db)
        return JSONResponse(content={"message": "Item Updated", "data": jsonable_encoder(item_db)},
                            status_code=status.HTTP_200_OK)


@sims_app.delete("/items/", summary="delete an item by id")
def delete_item(item_id: int):
    """
        Endpoint to delete an item by ID.
        Parameters:
        item_id (int): The ID of the item to be deleted.
        Returns:
        None.
        Raises:
        HTTPException: If no item with the given ID is found.
        """
    with SessionLocal() as db:
        item_db = db.query(Items).filter(Items.id == item_id).first()
        if not item_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item Not found"
            )
        db.delete(item_db)
        db.commit()
        return JSONResponse(content={"message": "Item Removed", "data": {}},
                            status_code=status.HTTP_200_OK)


@sims_app.post('/signup', summary="Create new user", response_model=AuthUser)
async def create_user(data: AuthUser):
    """
        Endpoint to create a new user.
        Parameters:
        data (AuthUser): The data of the user to be created, including name, email, and password.
        Returns:
        AuthUser: The data of the newly created user.
        Raises:
        HTTPException: If a user with the same email already exists.
        """
    db = SessionLocal()
    user = db.query(UserTable).filter_by(email=data.email).first()
    if user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exist"
        )

    user = {
        'name': data.name, 'password': get_hashed_password(data.password), 'email': data.email
    }

    user_db = UserTable(**user)
    db.add(user_db)
    db.commit()
    db.refresh(user_db)
    return user


@sims_app.post('/login', summary="user login", response_model=TokenSchema)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
        Endpoint for user login.
        Parameters:
        form_data (OAuth2PasswordRequestForm, optional): The form data containing the user's email and password. Default is None.
        Returns:
        TokenSchema: A JSON web token containing an access token and a refresh token.
        Raises:
        HTTPException: If the user is not found or the email and password do not match.
        """
    db = SessionLocal()
    user = db.query(UserTable).filter_by(name=form_data.username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found"
        )

    form_hashed_pass = get_hashed_password(form_data.password)
    if form_hashed_pass != user.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )

    return {
        "access_token": create_token(user.email),
        "refresh_token": refresh_token(user.email),
    }


@sims_app.get('/profit', summary="return details about the profit")
async def calculate_profit(user: AuthUser = Depends(get_current_user), start_date: date = Query(None), end_date: date = Query(None)):
    """
        Endpoint to calculate the profit earned from sold items.
        Parameters:
        user (AuthUser, optional): The authenticated user making the request. Default is the current user.
        Returns:
        JSONResponse: A JSON response containing a message and data about the profit earned for each item that has been sold.
        """
    with SessionLocal() as db:
        items = db.query(Items).filter(Items.sold_units > 0)
        if start_date:
            items = items.filter(Items.date >= start_date)
        if end_date:
            items = items.filter(Items.date <= end_date)
        return JSONResponse(
            content={"message": "Item Sold", "data": jsonable_encoder(profit_for_each_item(items=items.all()))},
            status_code=status.HTTP_200_OK)


@sims_app.put('/sell/', summary="End point to sell item")
def sell_item(item_name: str, quantity: Optional[int] = 1, user: AuthUser = Depends(get_current_user)):
    """
        End point to sell an item.
        Parameters:
        item_name (str): The name of the item to be sold.
        quantity (int, optional): The quantity of the item to be sold. Default is 1.
        user (AuthUser, optional): The authenticated user making the request. Default is the current user.
        Returns:
        JSONResponse: A JSON response containing a message and data if the item was sold successfully, or an error message if the item was not found, or there is not enough stock.
        Raises:
        HTTPException: If the item is not found or there is not enough stock.
    """
    with SessionLocal() as db:
        item_db = db.query(Items).filter(Items.name == item_name).first()
        if not item_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item Not found"
            )
        if item_db.quantity < quantity:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Not enough stock."
            )
        if item_db.status.lower() == "available":
            if item_db.quantity > 0:
                item_db.quantity -= quantity
                item_db.sold_units += quantity
                db.commit()
                db.refresh(item_db)
                return JSONResponse(content={"message": "Item Sold", "data": jsonable_encoder(item_db)},
                                    status_code=status.HTTP_200_OK)
            else:
                return JSONResponse(content={"message": "Out of stock", "data": {}},
                                    status_code=status.HTTP_200_OK)
        else:
            return JSONResponse(content={"message": "Out of stock", "data": {}},
                                status_code=status.HTTP_200_OK)
