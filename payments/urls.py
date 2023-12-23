# payments/urls.py

from django.urls import path

from . import views


app_name = "payments"
urlpatterns = [
    path('product/<int:product_id>', views.ProductView.as_view(), name='product'),
    path('create-checkout-session/<int:product_id>/', views.CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    path('config/<slug:slug>/', views.get_stripe_config, name='config'),
    path('success/', views.SuccessView.as_view()),
    path('cancelled/', views.CancelledView.as_view()),
    path('webhook/', views.stripe_webhook),

    path('products/', views.ProductListView.as_view(), name='product_list'),
]