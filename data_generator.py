from faker import Faker
from datetime import datetime, timedelta
import random
import json

# generate sample data
sample_customers_list = []
sample_orders_list = []
sample_products_list = []
sample_order_items_list = []


# generate customer data
faker = Faker()
for i in range(1,25):
    single_customer_data = {}
    single_customer_data['customer_id'] = i
    single_customer_data['name'] = faker.name()
    single_customer_data['email'] = f'{single_customer_data["name"].replace(" ","").lower()}' +\
                                        f'@{random.choice(["hotmail.com", "gmail.com", "coldmail.com"])}'
    single_customer_data['address'] = {'street': f"{random.randint(111,894)} {faker.street_name()}", 'city': f"{faker.city()}", 'state': faker.state()}
    # append to sample list
    sample_customers_list.append(single_customer_data)



# generate sample product list
product_names = ['Laptop', 'Phone', 'Tablet', 'Headphones', 'Smartwatch', 'Monitor',
                'Keyboard', 'Mouse', 'Gaming Chair', 'Desk Lamp', 'Router',
                'External Hard Drive', 'USB Flash Drive', 'Camera', 'Speakers',
                'Fitness Tracker', 'Microwave', 'Blender', 'Air Fryer',
                'Electric Kettle', 'Projector', 'Desk Organizer']
product_categories = ['Electronics', 'Electronics', 'Electronics', 'Accessories',
                       'Wearables', 'Electronics', 'Accessories', 'Accessories',
                       'Furniture', 'Lighting', 'Networking', 'Storage', 'Storage',
                       'Electronics', 'Audio', 'Wearables', 'Appliances', 'Appliances',
                       'Appliances', 'Appliances', 'Electronics', 'Furniture']
for i in range(101,123):
    sample_products_list.append({"product_id": i, "product_name": product_names[i-101], 
                                "category": product_categories[i-101], 
                                "price": random.randint(30,1200),
                                'stock_quantity': random.randint(20,90)})

for i in range(5001, 5030):
    single_order = {"order_id": i, "customer_id": random.randint(1,24), 
                    "order_date": datetime(2024, 1, 15,10, 0, 0) + timedelta(days=random.randint(0, 730)), 
                    "status": random.choice(["Delivered", "Pending"])
                   }

    if single_order["status"] == "Delivered":
        single_order["delivery_date"] = single_order["order_date"] + timedelta(days=random.randint(0, 7), hours=random.randint(2,24))
    
    sample_orders_list.append(single_order)


# Generate order items
order_item_id = 9001

for order in sample_orders_list:
    num_items = random.randint(1, 5)  # Each order has 1-5 items
    for _ in range(num_items):
        product = random.choice(sample_products_list)
        quantity = random.randint(1, 3)
        price = product["price"]
        sample_order_items_list.append({
            "order_item_id": order_item_id,
            "order_id": order["order_id"],
            "product_id": product["product_id"],
            "quantity": quantity,
            "price": price
        })
        order_item_id += 1


# Save data as json files

# Custom serializer for datetime
def custom_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()  # Convert datetime to ISO 8601 string
    raise TypeError("Type not serializable")

# Save customers sample data to JSON
with open("./sample_data/customers_collection.json", "w") as json_file:
    json.dump(sample_customers_list, json_file, indent=4, default=custom_serializer)

# Save orders sample data to JSON
with open("./sample_data/orders_collection.json", "w") as json_file:
    json.dump(sample_orders_list, json_file, indent=4, default=custom_serializer)

# Save products sample data to JSON
with open("./sample_data/products_collection.json", "w") as json_file:
    json.dump(sample_products_list, json_file, indent=4, default=custom_serializer)

# Save order_items sample data to JSON
with open("./sample_data/order_items_collection.json", "w") as json_file:
    json.dump(sample_order_items_list, json_file, indent=4, default=custom_serializer)


# summarizing results
print(f"customers: {len(sample_customers_list)}\nproducts: {len(sample_products_list)}\norders: {len(sample_orders_list)}\norder_items: {len(sample_order_items_list)}\n")
