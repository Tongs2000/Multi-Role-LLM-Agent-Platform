from app import app, db
from models import Product

def init_db():
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()

        # Add sample products
        products = [
            Product(name="Laptop", price=999.99, stock=10),
            Product(name="Smartphone", price=699.99, stock=15),
            Product(name="Headphones", price=149.99, stock=20),
            Product(name="Tablet", price=399.99, stock=8),
            Product(name="Smartwatch", price=249.99, stock=12)
        ]

        db.session.bulk_save_objects(products)
        db.session.commit()
        print("Database initialized with sample products")

if __name__ == '__main__':
    init_db()