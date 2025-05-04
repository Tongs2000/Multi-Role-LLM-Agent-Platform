from flask import Flask, jsonify

app = Flask(__name__)

# Mock database for products
products = [
    {"id": 1, "name": "Laptop", "price": 999.99, "inventory": 10},
    {"id": 2, "name": "Smartphone", "price": 699.99, "inventory": 15},
    {"id": 3, "name": "Headphones", "price": 149.99, "inventory": 20}
]

@app.route('/products', methods=['GET'])
def get_products():
    return jsonify(products)

if __name__ == '__main__':
    app.run(debug=True, port=5001)