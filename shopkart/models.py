from django.db import models
from django.contrib.auth.models import User



class Category(models.Model):
    title = models.CharField(max_length=100)
    
    def __str__(self):
        return self.title

class Product(models.Model):

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    title = models.CharField(max_length=100)
    price = models.IntegerField()
    details = models.TextField()
    image = models.ImageField(upload_to='products/')

    def __str__(self):
        return self.title
    
class Customer(models.Model):
    user_id = models.CharField(max_length=200)
    user_name = models.CharField(max_length=150)
    user_mobile = models.IntegerField()
    user_email = models.EmailField(max_length=250)
    user_password = models.CharField(max_length=128)
    user_address = models.TextField(max_length=300)
    profile_photo = models.ImageField(upload_to='profiles/', null=True, blank=True)
    address = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.user_name

class Cart(models.Model):
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return self.customer.user_name
    

class Wishlist(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
   

    def __str__(self):
        return f"{self.customer.user_name} - {self.product.title}"

class Order(models.Model):

    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Shipped', 'Shipped'),
        ('Out for Delivery', 'Out for Delivery'),
        ('Delivered', 'Delivered'),
    )

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    name = models.CharField(max_length=100)

    mobile = models.CharField(max_length=15)

    address = models.TextField()

    city = models.CharField(max_length=100)

    pincode = models.CharField(max_length=10)

    total_amount = models.IntegerField(default=0)

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.product.title
    
class Coupon(models.Model):

    code = models.CharField(max_length=50, unique=True)

    discount = models.IntegerField()

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code