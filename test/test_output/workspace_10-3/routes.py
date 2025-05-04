from flask import jsonify, request
from services import ProductService, CartService
from models import db

def init_routes(app):
    @app.route('/api/products', methods=['GET'])
    def get_products():
        products = ProductService.get_all_products()
        return jsonify(products)

    @app.route('/api/cart', methods=['GET'])
    def get_cart():
        cart_items = CartService.get_cart_items()
        total = CartService.calculate_total()
        return jsonify({
            'items': cart_items,
            'total': total
        })

    @app.route('/api/cart/add', methods=['POST'])
    def add_to_cart():
        data = request.get_json()
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)
        
        if not product_id:
            return jsonify({'error': 'Product ID is required'}), 400
        
        success = CartService.add_to_cart(product_id, quantity)
        if not success:
            return jsonify({'error': 'Product not found'}), 404
        
        return jsonify({'message': 'Item added to cart'}), 200

    @app.route('/api/cart/update', methods=['POST'])
    def update_cart():
        data = request.get_json()
        product_id = data.get('product_id')
        quantity = data.get('quantity')
        
        if not product_id or quantity is None:
            return jsonify({'error': 'Product ID and quantity are required'}), 400
        
        success = CartService.update_cart_item(product_id, quantity)
        if not success:
            return jsonify({'error': 'Item not found in cart'}), 404
        
        return jsonify({'message': 'Cart updated'}), 200

    @app.route('/api/cart/clear', methods=['POST'])
    def clear_cart():
        CartService.clear_cart()
        return jsonify({'message': 'Cart cleared'}), 200