from django.db import models
from django.contrib.auth.models import User


# ================= PRODUCT =================
class Product(models.Model):
    CATEGORY_CHOICES = (
        ('Men', 'Men'),
        ('Women', 'Women'),
        ('Kids', 'Kids'),
    )

    SUBCATEGORY_CHOICES = (
        ('Tshirt', 'Tshirt'),
        ('Shirt', 'Shirt'),
        ('Jeans', 'Jeans'),
        ('Watches', 'Watches'),
        ('Perfumes', 'Perfumes'),
        ('Hats', 'Hats'),

        ('Tops', 'Tops'),
        ('Dresses', 'Dresses'),
        ('Heels', 'Heels'),
        ('Bags', 'Bags'),
        ('Jewellery', 'Jewellery'),

        ('Kidswear', 'Kidswear'),
        ('Toys', 'Toys'),
        ('Shoes', 'Shoes'),
    )

    name = models.CharField(max_length=200)
    price = models.IntegerField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    subcategory = models.CharField(max_length=30, choices=SUBCATEGORY_CHOICES)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='products/')
    stock = models.IntegerField(default=0)

    is_featured = models.BooleanField(default=False)  # ✅ existing
    
    db_table= 'product'

    def __str__(self):
        return self.name


# ================= PRODUCT SIZE =================
class ProductSize(models.Model):
    SIZE_CHOICES = (
        ('XS', 'XS'),
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL'),
        ('XXL', 'XXL'),
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="sizes"   # ✅ important for template
    )
    size = models.CharField(max_length=5, choices=SIZE_CHOICES)
    price = models.IntegerField()

    class Meta:
        db_table = 'size'
        unique_together = ('product', 'size')  # ✅ prevents duplicate sizes

    def __str__(self):
        return f"{self.product.name} - {self.size}"


# ================= ORDER =================
# ================= ORDER =================
class Order(models.Model):

    STATUS_CHOICES = (

        ('Ordered', 'Ordered'),

        ('Packed', 'Packed'),

        ('Shipped', 'Shipped'),

        ('Out for Delivery', 'Out for Delivery'),

        ('Delivered', 'Delivered'),

    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    amount = models.FloatField()

    quantity = models.IntegerField(default=1)

    size = models.CharField(max_length=10, default="M")

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="Ordered"
    )

    ordered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ord'

    def __str__(self):

        return f"Order #{self.id}"


# ================= SELLER PROFILE =================
class SellerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to='profile_images/', default='default.png')
    
    class Meta:
        db_table='sellprofile'

    def __str__(self):
        return self.user.username


# ================= SIGNUP =================
class Signup(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=256)

    class Meta:
        db_table = 'signup'

    def __str__(self):
        return self.username
    
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
        db_table='wishlist'
        
# ================= CART =================
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=10)
    quantity = models.IntegerField(default=1)

    class Meta:
        db_table = 'cart'
        unique_together = ('user', 'product', 'size')

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


# ================= SHIPPING ADDRESS =================
class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    email = models.EmailField()
    phone = models.CharField(max_length=20)

    address = models.TextField()

    postal_code = models.CharField(max_length=20)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)

    total_amount = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'shipping_address'

    def __str__(self):
        return self.first_name
    
# ================= CONTACT MODEL =================
class Contact(models.Model):

    first_name = models.CharField(max_length=100)

    last_name = models.CharField(max_length=100)

    email = models.EmailField()

    phone = models.CharField(max_length=20)

    username = models.CharField(max_length=100)

    subject = models.CharField(max_length=200)

    message = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table='Contacts'

    def __str__(self):

        return f"{self.first_name} - {self.subject}"