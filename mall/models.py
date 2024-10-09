from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    city = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    
    def __str__(self):
        return self.user.username
    
class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Up to 10 digits, 2 decimal places
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    stock = models.IntegerField(default=0)  # Quantity available
    image = models.ImageField(upload_to='products/', null=True, blank=True)  # Upload product images
    
    def __str__(self):
        return self.name
    
    @property
    def is_in_stock(self):
        return self.stock > 0

# Model for order details
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    date_ordered = models.DateTimeField(default=timezone.now)
    complete = models.BooleanField(default=False)  # Marks if the order is paid and completed
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    
    def __str__(self):
        return f"Order {self.id} by {self.customer.user.username if self.customer else 'Guest'}"

    @property
    def get_cart_total(self):
        order_items = self.orderitem_set.all()
        total = sum([item.get_total for item in order_items])
        return total

    @property
    def get_cart_items(self):
        order_items = self.orderitem_set.all()
        total = sum([item.quantity for item in order_items])
        return total

# Model for each item in an order
class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    
    def __str__(self):
        return f"{self.quantity} of {self.product.name}"

    @property
    def get_total(self):
        return self.product.price * self.quantity

# Model to manage payment details via Flutterwave
class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Payment amount
    transaction_id = models.CharField(max_length=100, unique=True)
    flutterwave_payment_id = models.CharField(max_length=100, null=True, blank=True)
    payment_status = models.CharField(max_length=50, default='Pending')  # Can be 'Pending', 'Failed', 'Completed'
    date_paid = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Payment {self.transaction_id} for Order {self.order.id}"
    
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)  # For session-based carts
    date_created = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)  # Mark as completed once order is placed

    def __str__(self):
        return f"Cart for {self.user if self.user else 'Guest'}"

    @property
    def get_cart_total(self):
        items = self.cartitem_set.all()
        total = sum([item.get_total for item in items])
        return total

    @property
    def get_cart_items(self):
        items = self.cartitem_set.all()
        total = sum([item.quantity for item in items])
        return total
    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def get_total(self):
        return self.product.price * self.quantity
    
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} in {self.user.username}'s Wishlist"