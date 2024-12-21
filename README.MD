# MongoDB Project
This project demonstrates the implementation of a MongoDB-based e-commerce system, showcasing schema design decisions, transactional operations, real-time monitoring with change streams, and schema validation for data integrity.

## Schema Design Decisions
### Collections and Design Choices
1. **Customers Collection**
- **Design:** Embedded schema.
- **Reason:** A customer's address (e.g., street, city, state) is closely related to the customer and unlikely to change frequently or be queried independently.
- **Example:**
  ```json
    {
      "customer_id": 1,
      "name": "Teresa Gallegos",
      "email": "teresagallegos@coldmail.com",
      "address": {
          "street": "894 Valentine Lake",
          "city": "Ashleyville",
          "state": "Arizona"
          }
    }
  ```

2. **Products  Collection**
- **Design:** Referenced schema.
- **Reason:** Products are often reused across multiple orders and have stable data. Keeping them in a separate collection ensures consistency and reduces redundancy.
- **Example:**
  ```json
    {
        "product_id": 101,
        "product_name": "Laptop",
        "category": "Electronics",
        "price": 146,
        "stock_quantity": 61
    }
  ```


3. **Orders Collection**
- **Design:** Referenced schema.
- **Reason:** Orders involve a relationship with both customers and order items. Using references for `customer_id` allows efficient queries on customer orders without duplicating data.
- **Example:**
  ```json
    {
        "order_id": 5001,
        "customer_id": 3,
        "order_date": "2024-06-13T10:00:00",
        "status": "Delivered",
        "delivery_date": "2024-06-18T20:00:00"
    },
    {
        "order_id": 5002,
        "customer_id": 19,
        "order_date": "2024-09-07T10:00:00",
        "status": "Pending"
    }
  ```

4. **Order Items Collection**
- **Design:** Referenced schema.
- **Reason:** Order items represent a many-to-many relationship between orders and products. A referenced structure avoids duplicating product details across order items.
- **Example:**
  ```json
    {
        "order_item_id": 9001,
        "order_id": 5001,
        "product_id": 108,
        "quantity": 3,
        "price": 211
    }
  ```
### Indexes for Frequently Queried Fields
#### 1. Customers Collection
- **Index on `customer_id`:** Speeds up queries like fetching customer details or joining with orders.

#### 2. Products Collection
- **Index on `product_id`:** Optimizes lookups when joining with order items or querying product details.

#### 3. Orders Collection
- **Index on `customer_id`:** Accelerates customer order lookups
- **Index on `order_id`:**  Improves order-specific queries.

#### 4. Order Items Collection
- **Index on `order_id`:** Helps in retrieving items for a specific order.
- **Index on `product_id`:**  Speeds up revenue calculations and product-specific analysis.


## Project File Details

- **`data_generator.py`**: This script generates sample data for the four collections used in this project. The generated data is stored in the `sample_data` folder as JSON files:
  - `customers_collection.json` (24 documents)
  - `products_collection.json` (22 documents)
  - `order_items_collection.json` (96 documents)
  - `orders_collection.json` (29 documents)

  Since the sample data is already generated, you do not need to run the `data_generator.py` file again. The pre-generated data ensures reproducibility.

- **`MongoDB Project.ipynb`**: This Jupyter Notebook contains:
  - **Python scripts** for data insertion and manipulation.
  - **MongoDB queries** for analytical tasks and advanced operations.
  - **Aggregation pipelines** to address analytical questions.
  - **Schema Design explanations**, including the rationale for embedding vs. referencing and the indexes created.

## Steps to Run the Script
1. **Install Required Libraries** Ensure `pymongo` is installed for interacting with MongoDB:

    ```bash
    pip install pymongo
    ```
2. **Configure MongoDB**
- Set up a MongoDB instance locally or on a cloud provider (e.g., MongoDB Atlas).
- Create a database (`alt_ecommerce`) and collections (`customers`, `products`, `orders`, and `order_items`).

3. **Update the Connection String** Modify the `MongoDB Project.ipynb` code to include the connection string for your MongoDB instance. For security reasons, my connection string has been removed. Replace `"..."` with your connection string:
   ```python
    db_name = "alt_ecommerce"
    conn_str = "..." # insert your MongoDB connection string here
    try:
        client = MongoClient(conn_str)
        db = client[db_name]
        print(f"Connection to {db_name} done successfully ")
    except Exception as e:
        raise Exception(
            "The following error occurred: ", e) 
   ```
4. **Run the Script**
- Execute the Python script (`MongoDB Project.ipynb`) in a Jupyter Notebook environment or convert it to `.py` and run it:
```bash
python script.py
```

5. **Monitor Transactions**
- Use the provided `create_order` function to simulate transactional operations.

6. **Real-Time Monitoring**
- Use the change stream function to monitor real-time changes in the `orders` collection.

## Queries and Their Results
## Task 2: Analytical Queries
### 1. Which product categories generate the highest revenue?
- **Query:**
  ```python
    pipeline = [
        {
            '$lookup': {
                'from': "products", 
                'localField': "product_id", 
                'foreignField': "product_id", 
                'as': "product_details"
            }
        },
        {
            '$unwind': "$product_details"
        },
        {
            '$group': {
                '_id': "$product_details.category",
                'total_revenue': { '$sum': { '$multiply': ["$quantity", "$price"] } }
            }
        },
        {
            '$sort': { 'total_revenue': -1 }
        }
    ];

    result = list(order_items.aggregate(pipeline))

    print_results(result)
  ```
- **output:**
  ```json
  {"_id": "Appliances", "total_revenue": 25272}
  {"_id": "Electronics", "total_revenue": 24993}
  {"_id": "Wearables", "total_revenue": 15225}
  {"_id": "Storage", "total_revenue": 13110}
  {"_id": "Accessories", "total_revenue": 11762}
  {"_id": "Audio", "total_revenue": 8610}
  {"_id": "Lighting", "total_revenue": 8173}
  {"_id": "Networking", "total_revenue": 2589}
  {"_id": "Furniture", "total_revenue": 844}
  ```

### 2. What is the average delivery time for orders?
- **Query:**
  ```python
    pipeline = [
        {
            '$match': {
                'status': 'Delivered'  # Ensure only delivered orders are considered
            }
        },
        {
            '$project': {
                '_id': 0,
                'order_id': 1,
                'delivery_time_in_days': {
                    '$divide': [
                        { '$subtract': ["$delivery_date", "$order_date"] }, 
                        1000 * 60 * 60 * 24  #Convert milliseconds to days
                    ]
                }
            }
        },
        {
            '$group': {
                '_id': None,
                'average_delivery_time_in_days': { '$avg': "$delivery_time_in_days" }
            }
        }
    ];

    result = list(orders.aggregate(pipeline))
    print_results(result)
  ```
- **output:**
  ```json
  {"_id": None, "average_delivery_time_in_days": 3.8774509803921573}
  ```
### 3. Which states have the highest number of customers?
- **Query:**
  ```python
    pipeline = [
        {
            '$group': {
                '_id': "$address.state",  # Group by state
                'customer_count': { '$sum': 1 }  # Count customers in each state
            }
        },
        {
            '$sort': { 'customer_count': -1 }  # Sort in descending order
        }
    ];

    result = list(customers.aggregate(pipeline))
    print_results(result)
  ```
- **output:**
  ```json
    {"_id": "Arizona", "customer_count": 4}
    {"_id": "Colorado", "customer_count": 2}
    {"_id": "Tennessee", "customer_count": 2}
    {"_id": "New York", "customer_count": 2}
    {"_id": "Vermont", "customer_count": 1}
    {"_id": "Pennsylvania", "customer_count": 1}
    {"_id": "New Mexico", "customer_count": 1}
    {"_id": "West Virginia", "customer_count": 1}
    {"_id": "Georgia", "customer_count": 1}
    {"_id": "South Dakota", "customer_count": 1}
    {"_id": "North Dakota", "customer_count": 1}
    {"_id": "Alaska", "customer_count": 1}
    {"_id": "Connecticut", "customer_count": 1}
    {"_id": "Iowa", "customer_count": 1}
    {"_id": "Wyoming", "customer_count": 1}
    {"_id": "Mississippi", "customer_count": 1}
    {"_id": "Michigan", "customer_count": 1}
    {"_id": "Kansas", "customer_count": 1}
  ```

### 4. What are the top 3 most expensive products sold in each order?
- **Query:**
  ```python
    # Use $group to calculate revenue by category.

    pipeline = [
        {
            '$lookup': {
                'from': 'products',  # Join with the products collection
                'localField': 'product_id', 
                'foreignField': 'product_id', 
                'as': 'product_details'
            }
        },
        {
            '$unwind': '$product_details'  # Unpack the product details
        },
        {
            '$project': {
                'order_id': 1,
                'product_id': 1,
                'product_name': '$product_details.product_name',
                'category': '$product_details.category',
                'price': '$price'
            }
        },
        {
            '$sort': {
                'order_id': 1,  # Sort by order first
                'price': -1     # Then sort by price in descending order
            }
        },
        {
            '$group': {
                '_id': '$order_id',  # Group by order_id
                'top_products': { '$push': {
                    'product_id': '$product_id',
                    'product_name': '$product_name',
                    'price': '$price'
                }},
            }
        },
        {
            '$project': {
                'top_products': { '$slice': ['$top_products', 3] }  # Keep only the top 3
            }
        }
    ];

    result = list(order_items.aggregate(pipeline))

    print_results(result)
  ```
- **output:**
  ```json
    { "_id": 5014,
    "top_products": [ { "price": 907,
                        "product_id": 105,
                        "product_name": "Smartwatch"}]}
    { "_id": 5016,
    "top_products": [ { "price": 984,
                        "product_id": 107,
                        "product_name": "Keyboard"},
                        { "price": 636,
                        "product_id": 120,
                        "product_name": "Electric Kettle"},
                        { "price": 574,
                        "product_id": 115,
                        "product_name": "Speakers"}]}
    { "_id": 5002,
    "top_products": [ { "price": 1038,
                        "product_id": 119,
                        "product_name": "Air Fryer"},
                        {"price": 211, "product_id": 108, "product_name": "Mouse"}]}
    { "_id": 5022,
    "top_products": [ { "price": 743,
                        "product_id": 110,
                        "product_name": "Desk Lamp"},
                        { "price": 586,
                        "product_id": 106,
                        "product_name": "Monitor"}]}
    { "_id": 5007,
    "top_products": [ { "price": 1038,
                        "product_id": 119,
                        "product_name": "Air Fryer"},
                        { "price": 927,
                        "product_id": 104,
                        "product_name": "Headphones"},
                        {"price": 211, "product_id": 108, "product_name": "Mouse"}]}
    { "_id": 5029,
    "top_products": [ { "price": 782,
                        "product_id": 112,
                        "product_name": "External Hard Drive"},
                        { "price": 636,
                        "product_id": 120,
                        "product_name": "Electric Kettle"},
                        { "price": 586,
                        "product_id": 106,
                        "product_name": "Monitor"}]}
    { "_id": 5023,
    "top_products": [ { "price": 907,
                        "product_id": 105,
                        "product_name": "Smartwatch"},
                        { "price": 743,
                        "product_id": 110,
                        "product_name": "Desk Lamp"},
                        { "price": 743,
                        "product_id": 110,
                        "product_name": "Desk Lamp"}]}
    { "_id": 5017,
    "top_products": [ { "price": 1038,
                        "product_id": 119,
                        "product_name": "Air Fryer"},
                        { "price": 574,
                        "product_id": 115,
                        "product_name": "Speakers"}]}
    { "_id": 5028,
    "top_products": [ { "price": 644,
                        "product_id": 113,
                        "product_name": "USB Flash Drive"},
                        { "price": 644,
                        "product_id": 113,
                        "product_name": "USB Flash Drive"},
                        { "price": 635,
                        "product_id": 121,
                        "product_name": "Projector"}]}
    { "_id": 5027,
    "top_products": [ {"price": 863, "product_id": 111, "product_name": "Router"},
                        { "price": 574,
                        "product_id": 115,
                        "product_name": "Speakers"},
                        {"price": 211, "product_id": 108, "product_name": "Mouse"}]}
    { "_id": 5015,
    "top_products": [ { "price": 195,
                        "product_id": 118,
                        "product_name": "Blender"}]}
    { "_id": 5020,
    "top_products": [ {"price": 863, "product_id": 111, "product_name": "Router"},
                        { "price": 586,
                        "product_id": 106,
                        "product_name": "Monitor"},
                        { "price": 574,
                        "product_id": 115,
                        "product_name": "Speakers"}]}
    { "_id": 5024,
    "top_products": [ { "price": 907,
                        "product_id": 105,
                        "product_name": "Smartwatch"},
                        { "price": 907,
                        "product_id": 105,
                        "product_name": "Smartwatch"}]}
    { "_id": 5003,
    "top_products": [ {"price": 279, "product_id": 114, "product_name": "Camera"},
                        { "price": 279,
                        "product_id": 114,
                        "product_name": "Camera"}]}
    { "_id": 5019,
    "top_products": [{"price": 343, "product_id": 103, "product_name": "Tablet"}]}
    { "_id": 5005,
    "top_products": [ { "price": 1038,
                        "product_id": 119,
                        "product_name": "Air Fryer"},
                        { "price": 644,
                        "product_id": 113,
                        "product_name": "USB Flash Drive"},
                        { "price": 202,
                        "product_id": 116,
                        "product_name": "Fitness Tracker"}]}
    { "_id": 5021,
    "top_products": [ { "price": 1038,
                        "product_id": 119,
                        "product_name": "Air Fryer"},
                        { "price": 782,
                        "product_id": 112,
                        "product_name": "External Hard Drive"},
                        { "price": 574,
                        "product_id": 115,
                        "product_name": "Speakers"}]}
    { "_id": 5025,
    "top_products": [ { "price": 927,
                        "product_id": 104,
                        "product_name": "Headphones"},
                        { "price": 743,
                        "product_id": 110,
                        "product_name": "Desk Lamp"},
                        { "price": 202,
                        "product_id": 116,
                        "product_name": "Fitness Tracker"}]}
    { "_id": 5026,
    "top_products": [ { "price": 586,
                        "product_id": 106,
                        "product_name": "Monitor"}]}
    { "_id": 5009,
    "top_products": [ { "price": 743,
                        "product_id": 110,
                        "product_name": "Desk Lamp"},
                        {"price": 279, "product_id": 114, "product_name": "Camera"},
                        { "price": 195,
                        "product_id": 118,
                        "product_name": "Blender"}]}
    { "_id": 5001,
    "top_products": [ {"price": 343, "product_id": 103, "product_name": "Tablet"},
                        {"price": 279, "product_id": 114, "product_name": "Camera"},
                        {"price": 211, "product_id": 108, "product_name": "Mouse"}]}
    { "_id": 5004,
    "top_products": [ {"price": 863, "product_id": 111, "product_name": "Router"},
                        { "price": 586,
                        "product_id": 106,
                        "product_name": "Monitor"},
                        { "price": 574,
                        "product_id": 115,
                        "product_name": "Speakers"}]}
    { "_id": 5010,
    "top_products": [ { "price": 1038,
                        "product_id": 119,
                        "product_name": "Air Fryer"},
                        { "price": 984,
                        "product_id": 107,
                        "product_name": "Keyboard"}]}
    { "_id": 5006,
    "top_products": [ { "price": 927,
                        "product_id": 104,
                        "product_name": "Headphones"},
                        { "price": 907,
                        "product_id": 105,
                        "product_name": "Smartwatch"},
                        { "price": 782,
                        "product_id": 112,
                        "product_name": "External Hard Drive"}]}
    { "_id": 5011,
    "top_products": [ { "price": 1038,
                        "product_id": 119,
                        "product_name": "Air Fryer"},
                        {"price": 211, "product_id": 108, "product_name": "Mouse"},
                        { "price": 146,
                        "product_id": 101,
                        "product_name": "Laptop"}]}
    { "_id": 5018,
    "top_products": [ { "price": 927,
                        "product_id": 104,
                        "product_name": "Headphones"},
                        { "price": 636,
                        "product_id": 120,
                        "product_name": "Electric Kettle"},
                        { "price": 635,
                        "product_id": 121,
                        "product_name": "Projector"}]}
    { "_id": 5008,
    "top_products": [ { "price": 782,
                        "product_id": 112,
                        "product_name": "External Hard Drive"},
                        {"price": 758, "product_id": 102, "product_name": "Phone"},
                        { "price": 343,
                        "product_id": 103,
                        "product_name": "Tablet"}]}
    { "_id": 5012,
    "top_products": [ { "price": 1038,
                        "product_id": 119,
                        "product_name": "Air Fryer"},
                        { "price": 574,
                        "product_id": 115,
                        "product_name": "Speakers"},
                        { "price": 211,
                        "product_id": 109,
                        "product_name": "Gaming Chair"}]}
    { "_id": 5013,
    "top_products": [ { "price": 635,
                        "product_id": 121,
                        "product_name": "Projector"},
                        {"price": 343, "product_id": 103, "product_name": "Tablet"},
                        { "price": 146,
                        "product_id": 101,
                        "product_name": "Laptop"}]}
  ```

## Task 4: Advanced Features
### 1. Implement Transactions: Simulate an order creation process that updates the orders and inventory collections atomically.
- **Query:**
  ```python
    # Start a transaction
    def create_order(customer_id, items):
        """
        Simulates an order creation process that updates the `orders`, `order_items`, 
        and `products` collections atomically using a MongoDB transaction.

        Parameters
        ----------
        customer_id : int
            The ID of the customer placing the order.
        items : dict
            A dictionary where each key is a `product_id` (int) and the corresponding 
            value is the `quantity` (int) of that product being ordered.
        """
        session = client.start_session()
        try:
            session.start_transaction()

            # Step 1: Add the order to the orders collection
            max_order = orders.find_one(sort=[("order_id", -1)])
            max_order_id = max_order["order_id"] if max_order else 5000  # Default initial order ID
            order_id = max_order_id + 1

            orders.insert_one({
                "order_id": order_id,
                "customer_id": customer_id,
                "order_date": datetime.now(),
                "status": "Pending"
            }, session=session)

            # Step 2: Add items to the order_items collection and update stock
            for product_id, quantity in items.items():
                # Fetch product details
                product = products.find_one({"product_id": product_id}, {"price": 1, "stock_quantity": 1, "_id": 0})
                if not product:
                    raise ValueError(f"Product with ID {product_id} does not exist.")
                if product["stock_quantity"] < quantity:
                    raise ValueError(f"Insufficient stock for product ID {product_id}. Available: {product['stock_quantity']}, Requested: {quantity}.")

                # Generate order_item_id
                max_order_item = order_items.find_one(sort=[("order_item_id", -1)])
                max_order_item_id = max_order_item["order_item_id"] if max_order_item else 9000  # Default initial order item ID
                order_item_id = max_order_item_id + 1

                # Insert order item
                order_items.insert_one({
                    "order_item_id": order_item_id,
                    "order_id": order_id,
                    "product_id": product_id,
                    "quantity": quantity,
                    "price": product["price"]
                }, session=session)

                # Update stock quantity
                products.update_one({"product_id": product_id}, {"$inc": {"stock_quantity": -quantity}}, session=session)

            # Commit the transaction
            session.commit_transaction()
            print(f"Order {order_id} created successfully.")

        except (OperationFailure, ValueError) as e:
            # Abort the transaction in case of failure
            session.abort_transaction()
            print(f"Transaction failed: {e}")
        finally:
            session.end_session()
  ```
  ```python
    # make an order
    create_order(customer_id=4, items = {103:2, 104:3})

    # fetch the last order
    orders.find_one(sort=[("order_id", -1)])
  ```
- **output:**
  ```bash
    Order 5030 created successfully.
    {"_id": ObjectId("67660ef626f3a1f9ee88771b"),
    "order_id": 5030,
    "customer_id": 4,
    "order_date": datetime.datetime(2024, 12, 21, 1, 42, 30, 891000),
    "status": "Pending"}
  ```

### 2. Use Change Streams: Monitor real-time changes in the orders collection.
- **Query:**
  ```python
    import threading

    # function to monitor changes
    def monitor_orders():
        with orders.watch() as stream:
            for change in stream:
                print(f"Change detected: {change}")

    # start monitoring in a separate thread
    monitor_thread = threading.Thread(target=monitor_orders, daemon=True)
    monitor_thread.start()
    
    # Add a new order to trigger a change
    create_order(customer_id=2, items = {110:3})
  ```
- **output:**
  ```bash
    Change detected: {"txnNumber": 1, "lsid": {"id": Binary(b"\xfe\x8d\xaaQUxO\xad\x94\x19yu\xa7\xc4\x10\xfa", 4), "uid": b"u\xda\xa8\xb7\xaf/.\x90T>s\xae\xa8X\xf6q\xd0\xa5\xbf\xf7o\xfe\xf1}eT\xb0\x92v\x07\x12\xc1"}, "_id": {"_data": "8267660EFA000000072B042C0100296E5A10044FBC040D1CC14A7A847EEBD4E9C10F78463C6F7065726174696F6E54797065003C696E736572740046646F63756D656E744B65790046645F6964006467660EF926F3A1F9EE88771E000004"}, "operationType": "insert", "clusterTime": Timestamp(1734741754, 7), "wallTime": datetime.datetime(2024, 12, 21, 0, 42, 34, 470000), "fullDocument": {"_id": ObjectId("67660ef926f3a1f9ee88771e"), "order_id": 5031, "customer_id": 2, "order_date": datetime.datetime(2024, 12, 21, 1, 42, 33, 423000), "status": "Pending"}, "ns": {"db": "alt_ecommerce", "coll": "orders"}, "documentKey": {"_id": ObjectId("67660ef926f3a1f9ee88771e")}}
    Order 5031 created successfully.
  ```


### 3. Apply Schema Validation: Ensure all documents in the products collection include a valid price.
- **Query:**
  ```python
    schema = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["product_id", "product_name", "category", "price", "stock_quantity"],
            "properties": {
                "product_id": {"bsonType": "int"},
                "product_name": {"bsonType": "string"},
                "category": {"bsonType": "string"},
                "price": {
                    "bsonType": "double",
                    "minimum": 0,
                    "description": "Price must be a positive number"
                    },
                "stock_quantity": {
                    "bsonType": "int",
                    "minimum": 0,
                    "description": "inventory must be a positive number"
                    }
            }
        }
    }

    # Apply the schema validation
    db.command({
        "collMod": "products",
        "validator": schema,
        "validationLevel": "strict"
    })
    print("Schema validation applied to the products collection.")

  ```
- **output:**
  ```bash
    Schema validation applied to the products collection.
  ```