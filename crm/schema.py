import re
import graphene
from graphene_django import DjangoObjectType
from django.db import transaction
from django.core.exceptions import ValidationError
from graphene_django.filter import DjangoFilterConnectionField

from crm.models import Customer, Product, Order
from crm.filters import CustomerFilter, ProductFilter, OrderFilter


# ==========================
# GraphQL Types
# ==========================
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        interfaces = (graphene.relay.Node,)
        filterset_class = CustomerFilter   # ✅ connect custom filter


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        interfaces = (graphene.relay.Node,)
        filterset_class = ProductFilter    # ✅ connect custom filter


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        interfaces = (graphene.relay.Node,)
        filterset_class = OrderFilter      # ✅ connect custom filter


# ==========================
# Input Types
# ==========================
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()


# ==========================
# Mutations
# ==========================
class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String(required=False)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, name, email, phone=None):
        if Customer.objects.filter(email=email).exists():
            raise Exception("Email already exists")

        if phone and not re.match(r"^\+?\d{7,15}$|^\d{3}-\d{3}-\d{4}$", phone):
            raise Exception("Invalid phone format. Use +1234567890 or 123-456-7890")

        customer = Customer.objects.create(name=name, email=email, phone=phone)
        return CreateCustomer(customer=customer, message="Customer created successfully!")


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        customers = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @transaction.atomic
    def mutate(self, info, customers):
        created = []
        errors = []

        for c in customers:
            try:
                if Customer.objects.filter(email=c.email).exists():
                    raise ValidationError(f"Email already exists: {c.email}")
                if c.phone and not re.match(r"^\+?\d{7,15}$|^\d{3}-\d{3}-\d{4}$", c.phone):
                    raise ValidationError(f"Invalid phone: {c.phone}")

                customer = Customer.objects.create(
                    name=c.name,
                    email=c.email,
                    phone=c.phone
                )
                created.append(customer)
            except Exception as e:
                errors.append(str(e))

        return BulkCreateCustomers(customers=created, errors=errors)


class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Float(required=True)
        stock = graphene.Int(required=False, default_value=0)

    product = graphene.Field(ProductType)

    def mutate(self, info, name, price, stock):
        if price <= 0:
            raise Exception("Price must be positive")
        if stock < 0:
            raise Exception("Stock cannot be negative")

        product = Product.objects.create(name=name, price=price, stock=stock)
        return CreateProduct(product=product)


class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.ID, required=True)

    order = graphene.Field(OrderType)

    def mutate(self, info, customer_id, product_ids):
        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            raise Exception("Invalid customer ID")

        if not product_ids:
            raise Exception("At least one product must be selected")

        products = Product.objects.filter(id__in=product_ids)
        if products.count() != len(product_ids):
            raise Exception("One or more invalid product IDs")

        total_amount = sum([p.price for p in products])

        order = Order.objects.create(customer=customer, total_amount=total_amount)
        order.products.set(products)
        order.save()

        return CreateOrder(order=order)


class UpdateLowStockProducts(graphene.Mutation):
    products = graphene.List(lambda: ProductType)
    message = graphene.String()

    def mutate(self, info):
        # Find products with stock < 10
        low_stock_products = Product.objects.filter(stock__lt=10)

        updated_products = []
        for product in low_stock_products:
            product.stock += 10  # Simulate restocking
            product.save()
            updated_products.append(product)

        message = "Low stock products updated successfully." if updated_products else "No low stock products found."

        return UpdateLowStockProducts(products=updated_products, message=message)


# ==========================
# Queries
# ==========================
class Query(graphene.ObjectType):
    customer = graphene.relay.Node.Field(CustomerType)
    product = graphene.relay.Node.Field(ProductType)
    order = graphene.relay.Node.Field(OrderType)

    all_customers = DjangoFilterConnectionField(CustomerType)
    all_products = DjangoFilterConnectionField(ProductType)
    all_orders = DjangoFilterConnectionField(OrderType)




# ==========================
# Root Mutation
# ==========================
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
    update_low_stock_products = UpdateLowStockProducts.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)