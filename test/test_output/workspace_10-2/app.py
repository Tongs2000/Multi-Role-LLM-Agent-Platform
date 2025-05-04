from flask import Flask, request, jsonify
from uuid import uuid4
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from db import get_db_connection

app = Flask(__name__)

# Initialize database connection
conn = get_db_connection()
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price FLOAT NOT NULL,
    description TEXT,
    image_url VARCHAR(255),
    stock INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS carts (
    user_id UUID PRIMARY KEY,
    items JSONB,
    total_price FLOAT
);

CREATE TABLE IF NOT EXISTS orders (
    id UUID PRIMARY KEY,
    user_id UUID,
    items JSONB,
    total_price FLOAT,
    status VARCHAR(50),
    timestamp TIMESTAMP
);
""")
conn.commit()

# Helper function to calculate total price
def calculate_total_price(items):
    total = 0.0
    for item in items:
        cursor.execute("SELECT price FROM products WHERE id = %s", (item["productId"],))
        product = cursor.fetchone()
        if product:
            total += product["price"] * item["quantity"]
    return total

# API Endpoints
@app.route('/api/products', methods=['GET'])
def get_products():
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    return jsonify(products)

@app.route('/api/products/<string:product_id>', methods=['GET'])
def get_product(product_id):
    cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    product = cursor.fetchone()
    if product:
        return jsonify(product)
    return jsonify({"error": "Product not found"}), 404

@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    product_id = data.get("productId")
    quantity = data.get("quantity", 1)

    cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    product = cursor.fetchone()
    if not product:
        return jsonify({"error": "Product not found"}), 404
    if product["stock"] < quantity:
        return jsonify({"error": "Insufficient stock"}), 400

    user_id = data.get("userId", str(uuid4()))
    cursor.execute("SELECT * FROM carts WHERE user_id = %s", (user_id,))
    cart = cursor.fetchone()

    if not cart:
        cursor.execute(
            "INSERT INTO carts (user_id, items, total_price) VALUES (%s, %s, %s)",
            (user_id, [], 0.0)
        )
        conn.commit()
        cart = {"user_id": user_id, "items": [], "total_price": 0.0}

    items = cart["items"]
    existing_item = next((item for item in items if item["productId"] == product_id), None)
    if existing_item:
        existing_item["quantity"] += quantity
    else:
        items.append({"productId": product_id, "quantity": quantity})

    total_price = calculate_total_price(items)
    cursor.execute(
        "UPDATE carts SET items = %s, total_price = %s WHERE user_id = %s",
        (items, total_price, user_id)
    )
    conn.commit()
    return jsonify({"user_id": user_id, "items": items, "total_price": total_price})

@app.route('/api/cart/update', methods=['PUT'])
def update_cart():
    data = request.get_json()
    user_id = data.get("userId")
    product_id = data.get("productId")
    quantity = data.get("quantity")

    cursor.execute("SELECT * FROM carts WHERE user_id = %s", (user_id,))
    cart = cursor.fetchone()
    if not cart:
        return jsonify({"error": "Cart not found"}), 404

    items = cart["items"]
    item = next((item for item in items if item["productId"] == product_id), None)
    if not item:
        return jsonify({"error": "Item not found in cart"}), 404

    cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    product = cursor.fetchone()
    if not product:
        return jsonify({"error": "Product not found"}), 404
    if product["stock"] < quantity:
        return jsonify({"error": "Insufficient stock"}), 400

    item["quantity"] = quantity
    total_price = calculate_total_price(items)
    cursor.execute(
        "UPDATE carts SET items = %s, total_price = %s WHERE user_id = %s",
        (items, total_price, user_id)
    )
    conn.commit()
    return jsonify({"user_id": user_id, "items": items, "total_price": total_price})

@app.route('/api/cart/remove', methods=['DELETE'])
def remove_from_cart():
    data = request.get_json()
    user_id = data.get("userId")
    product_id = data.get("productId")

    cursor.execute("SELECT * FROM carts WHERE user_id = %s", (user_id,))
    cart = cursor.fetchone()
    if not cart:
        return jsonify({"error": "Cart not found"}), 404

    items = [item for item in cart["items"] if item["productId"] != product_id]
    total_price = calculate_total_price(items)
    cursor.execute(
        "UPDATE carts SET items = %s, total_price = %s WHERE user_id = %s",
        (items, total_price, user_id)
    )
    conn.commit()
    return jsonify({"user_id": user_id, "items": items, "total_price": total_price})

@app.route('/api/cart', methods=['GET'])
def get_cart():
    user_id = request.args.get("userId")
    cursor.execute("SELECT * FROM carts WHERE user_id = %s", (user_id,))
    cart = cursor.fetchone()
    if not cart:
        return jsonify({"error": "Cart not found"}), 404
    return jsonify(cart)

@app.route('/api/checkout', methods=['POST'])
def checkout():
    data = request.get_json()
    user_id = data.get("userId")

    cursor.execute("SELECT * FROM carts WHERE user_id = %s", (user_id,))
    cart = cursor.fetchone()
    if not cart or not cart["items"]:
        return jsonify({"error": "Cart is empty"}), 400

    for item in cart["items"]:
        cursor.execute("SELECT * FROM products WHERE id = %s", (item["productId"],))
        product = cursor.fetchone()
        if not product or product["stock"] < item["quantity"]:
            return jsonify({"error": "Product unavailable or insufficient stock"}), 400
        cursor.execute(
            "UPDATE products SET stock = stock - %s WHERE id = %s",
            (item["quantity"], item["productId"])
        )

    order = {
        "id": str(uuid4()),
        "user_id": user_id,
        "items": cart["items"],
        "total_price": cart["total_price"],
        "status": "Pending",
        "timestamp": datetime.now().isoformat()
    }
    cursor.execute(
        "INSERT INTO orders (id, user_id, items, total_price, status, timestamp) VALUES (%s, %s, %s, %s, %s, %s)",
        (order["id"], order["user_id"], order["items"], order["total_price"], order["status"], order["timestamp"])
    )
    cursor.execute("DELETE FROM carts WHERE user_id = %s", (user_id,))
    conn.commit()
    return jsonify(order)

if __name__ == '__main__':
    app.run(debug=True)