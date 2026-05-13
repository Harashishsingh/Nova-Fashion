from django.contrib import admin
from .models import Product, Order, SellerProfile, Signup, ProductSize
from .models import *


# ================= PRODUCT SIZE INLINE =================
class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 1


# ================= PRODUCT ADMIN =================
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductSizeInline]


# ✅ Correct way to register Product with inline
admin.site.register(Product, ProductAdmin)


# ================= OTHER MODELS =================
admin.site.register(Order)
admin.site.register(SellerProfile)


# ================= SIGNUP ADMIN =================
@admin.register(Signup)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'first_name', 'last_name', 'email')
    
admin.site.register(Cart)
admin.site.register(ShippingAddress)
admin.site.register(Contact)