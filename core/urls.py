from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('accounts/', views.accounts, name='accounts'),
    path('logout/', views.logout_view, name='logout'),
    path('report/', views.report_item, name='report'),
    path('items/', views.items, name='items'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('item/<int:item_id>/', views.item_detail, name='item_detail'),
    path('claim/<int:item_id>/', views.claim_item, name='claim'),
    path('claim/<int:claim_id>/update/', views.update_claim, name='update_claim'),
    path('item/<int:item_id>/resolve/', views.resolve_item, name='resolve_item'),
    path('item/<int:item_id>/delete/', views.delete_item, name='delete_item'),
]
