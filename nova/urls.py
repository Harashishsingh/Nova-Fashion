from django.contrib import admin
from django.urls import path
from main import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Homepage
    path('', views.index, name='home'),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('logout/', views.signout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('products/<str:category>/<str:subcategory>/', views.product_page, name='product_page'),

    # Product CRUD
    path('delete/<int:id>/', views.delete_product, name='delete_product'),
    path('update/<int:id>/', views.update_product, name='update_product'),

    # Profile
    path('update-profile-image/', views.update_profile_image, name='update_profile_image'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    # urls.py

path('product/<int:id>/', views.product_detail, name='product_detail'),
path('search/', views.search_products, name='search_products'),
path('favorites/', views.wishlist_view, name='wishlist_view'),
    path('add-to-wishlist/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove-from-wishlist/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('about',views.about),
    path('contact',views.contact),
    # CART
path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
path('cart/', views.cart_view, name='cart_view'),
path('increase-cart/<int:cart_id>/', views.increase_cart, name='increase_cart'),
path('decrease-cart/<int:cart_id>/', views.decrease_cart, name='decrease_cart'),
path('remove-cart/<int:cart_id>/', views.remove_cart, name='remove_cart'),

# ORDER
path('order-page/', views.order_page, name='order_page'),
path('payment-page/', views.payment_page, name='payment_page'),
path('contact/',views.contact,name='contact'),
path('my-orders/', views.my_orders, name='my_orders'),

]

# Serve media files during development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)