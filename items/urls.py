from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('items/', views.item_list, name='item_list'),
    path('items/<int:pk>/', views.item_detail, name='item_detail'),
    path('items/lost/report/', views.report_lost_item, name='report_lost_item'),
    path('items/found/report/', views.report_found_item, name='report_found_item'),
    path('items/<int:pk>/claim/', views.claim_item, name='claim_item'),
    path('items/<int:pk>/update/', views.update_item, name='update_item'),
    path('items/<int:pk>/delete/', views.delete_item, name='delete_item'),
    path('items/<int:pk>/return/', views.mark_returned, name='mark_returned'),
    path('items/<int:pk>/share/', views.share_item, name='share_item'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('claims/<int:pk>/approve/', views.approve_claim, name='approve_claim'),
    path('claims/<int:pk>/reject/', views.reject_claim, name='reject_claim'),
    path('statistics/', views.statistics, name='statistics'),
    path('success-dashboard/', views.success_dashboard, name='success_dashboard'),
    path('select-location/', views.select_location, name='select_location'),
    path('api/items-by-date/', views.api_items_by_date, name='api_items_by_date'),
]
