## Shop Inventory System
This is a shop inventory system that allows you to keep track of your product inventory and sales/profit. With this system, you can easily add new products, track inventory levels, and view sales data.

### Features
**Add new products:** You can add new products to your inventory with a name, description, cost, and price.
**Track inventory levels:** You can track the quantity of each product in your inventory and view alerts when the quantity falls below a certain level.
**Generate reports:** You can generate reports that provide an overview of your inventory and sales data to check on profits.

### Getting Started
To get started with this system, you will need to have Python installed on your computer. Once you have Python installed, you can follow these steps:

* Extract the ZIP file to you system.*
* Create a new virtual environment by running python -m venv env in the terminal.*
* Activate the virtual environment by running source env/bin/activate (Unix/Mac) or env\Scripts\activate (Windows) in the terminal.*
* Install the required dependencies by running pip install -r requirements.txt in the terminal.*
* Start the system by running python main.py in the terminal. Or you can do the env setup in pycharm and ru from there.*

### Usage
Once you have started the system, you can open the browser and go to http://127.0.0.1:8000/docs#/ it will list down all the api endpoints which are implemented:

* POST /items: Add a new product to the inventory.
* GET /items: List all the products in the inventory.
* GET /item: List one item based on the filter/search needed. The `options` parameter takes the name of the table in case of description and name, for price, available options are <, >, =, <=, >=. In case of name or description set as options, search_term would be the text which will be match. The text is case-insensitive. In case of price set as option, we will pass an FLOAT value in search_term.
* PUT /sell/<item_name>: This api is locked behind authentication. Sells a product from the inventory based on the name of the product. It takes the exact name of the product and quantity. Name is required whereas, the quantity is optional set to default 1.
* UPDATE /items/<item_id>: Updates item based on the id. id is required and rest of the params are optional. If any param is missing it will use the existing value.
* DELETE /items/<item_id>: Deletes item based on id.
* GET /profit: This api is locked behind authentication. Calculates the profit report and send json in response.

## Run the project using Docker containers and forcing build containers
*Using docker compose command*
```sh
docker compose -f docker-compose-dev.yml up --build
```
*Using Makefile command*
```sh
make run-dev-build
```

## Run project using Docker container
*Using docker compose command*
```sh
docker compose -f docker-compose-dev.yml up
```

*Using Makefile command*
```sh
make run-dev
```

## Setup database with initial data
This creates sample users on database.
*Using docker compose command*
```
docker compose -f docker-compose-dev.yml exec fastapi_server python app/initial_data.py
