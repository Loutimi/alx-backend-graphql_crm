import os
import django
import random
from datetime import datetime

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alx_backend_graphql_crm.settings")
django.setup()

from crm.models import Customer, Product, Order


def seed_customers():
    customers_data = [
        {"name": "Alice", "email": "alice@example.com", "phone": "+1234567890"},
        {"name": "Bob", "email": "bob@example.com", "phone": "123-456-7890"},
        {"name": "Carol", "email": "carol@example.com"},
        {"name": "David", "email": "david@example.com"},
    ]

    for c in customers_data:
        customer, created = Customer.objects.get_or_create(email=c["email"], defaults=c)
        if created:
            print(f"Created customer: {customer.name}")
        else:
            print(f"Customer already exists: {customer.name}")


def seed_products():
    products_data = [
        {"name": "Laptop", "price": 999.99, "stock": 10},
        {"name": "Phone", "price": 499.99, "stock": 25},
        {"name": "Headphones", "price": 199.99, "stock": 50},
        {"name": "Monitor", "price": 299.99, "stock": 15},
    ]

    for p in products_data:
        product, created = Product.objects.get_or_create(name=p["name"], defaults=p)
        if created:
            print(f"Created product: {product.name}")
        else:
            print(f"Product already exists: {product.name}")


def seed_orders():
    customers = list(Customer.objects.all())
    products = list(Product.objects.all())

    if not customers or not products:
        print("Seed customers and products before creating orders.")
        return

    for i in range(5):
        customer = random.choice(customers)
        selected_products = random.sample(products, random.randint(1, len(products)))

        total_amount = sum([p.price for p in selected_products])
        order = Order.objects.create(
            customer=customer, total_amount=total_amount, order_date=datetime.now()
        )
        order.products.set(selected_products)
        print(f"Created order {order.id} for {customer.name} (${total_amount:.2f})")


if __name__ == "__main__":
    print("Seeding database...")
    seed_customers()
    seed_products()
    seed_orders()
    print("Seeding complete!")
