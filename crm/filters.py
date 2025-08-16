import django_filters
from .models import Customer, Product, Order

class CustomerFilter(django_filters.FilterSet):
    name_icontains = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    created_at_gte = django_filters.DateFilter(field_name="created_at", lookup_expr="gte")

    class Meta:
        model = Customer
        fields = ["name_icontains", "created_at_gte"]


class ProductFilter(django_filters.FilterSet):
    price_gte = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    price_lte = django_filters.NumberFilter(field_name="price", lookup_expr="lte")

    class Meta:
        model = Product
        fields = ["price_gte", "price_lte", "stock"]


class OrderFilter(django_filters.FilterSet):
    customer_name = django_filters.CharFilter(field_name="customer__name", lookup_expr="icontains")
    product_name = django_filters.CharFilter(field_name="product__name", lookup_expr="icontains")
    total_amount_gte = django_filters.NumberFilter(field_name="total_amount", lookup_expr="gte")

    class Meta:
        model = Order
        fields = ["customer_name", "product_name", "total_amount_gte"]
