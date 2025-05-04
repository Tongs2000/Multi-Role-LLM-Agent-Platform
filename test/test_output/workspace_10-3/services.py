from models import db, Product, Cart

class ProductService:
    @staticmethod
    def get_all_products():
        return Product.query.all()

    @staticmethod
    def get_product_by_id(product_id):
        return Product.query.get(product_id)

class CartService:
    @staticmethod
    def get_cart_items():
        return Cart.query.all()

    @staticmethod
    def add_to_cart(product_id, quantity=1):
        product = ProductService.get_product_by_id(product_id)
        if not product:
            return False
        
        cart_item = Cart.query.filter_by(product_id=product_id).first()
        if cart_item:
            cart_item.quantity += quantity
        else:
            cart_item = Cart(product_id=product_id, quantity=quantity)
            db.session.add(cart_item)
        
        db.session.commit()
        return True

    @staticmethod
    def update_cart_item(product_id, quantity):
        cart_item = Cart.query.filter_by(product_id=product_id).first()
        if not cart_item:
            return False
        
        if quantity <= 0:
            db.session.delete(cart_item)
        else:
            cart_item.quantity = quantity
        
        db.session.commit()
        return True

    @staticmethod
    def calculate_total():
        cart_items = Cart.query.join(Product).all()
        return sum(item.product.price * item.quantity for item in cart_items)

    @staticmethod
    def clear_cart():
        Cart.query.delete()
        db.session.commit()