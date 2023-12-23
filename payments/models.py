from _decimal import Decimal
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Item(models.Model):
    CUR = (
        ('USD', 'USD'),
        ('EUR', 'EUR'),
    )
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    price = models.FloatField(null=True)
    currency = models.CharField(max_length=10, default='USD', choices=CUR)

    def __str__(self):
        return str(self.name)


class Discount(models.Model):
    name = models.CharField(max_length=30, unique=True, )
    percent = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(99)])

    def __str__(self):
        return str(self.name) + ' is ' + f'{self.percent}%'


class Tax(models.Model):
    value = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)])
    name = models.CharField(max_length=30, unique=True)
    stripe_id = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return str(self.name) + ' - ' + f'{self.value}%'


class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    is_paid = models.BooleanField(default=False, verbose_name='Payment status')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)
    tax = models.ForeignKey(Tax, null=True, default=None, on_delete=models.SET_DEFAULT)
    discount = models.ForeignKey(Discount, null=True, default=None, on_delete=models.SET_DEFAULT)

    class Meta:
        ordering = ('-created',)

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())

    def __str__(self):
        return str(self.id)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Item, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'Product:{self.product}'

    def get_cost(self):
        return self.price * self.quantity
