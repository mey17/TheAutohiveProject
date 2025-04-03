from django.urls import path, include
from django.conf import settings
from . import views
from django.conf.urls.static import static


urlpatterns = [
    path('', views.index, name='index'),
    path('view_parking_place/<int:place_id>/', views.view_parking_place, name='view_parking_place'),
    path('view_parking_lot/', views.view_parking_place, name='view_parking_lot'), 
    path('letspark/', views.parking_reservation, name='parking_reservation'),
    path('account/', views.account_details, name='account'),
    path('add_parking_place/', views.add_parking_place, name='add_parking_place'),
    path('verify-email/', views.verification_page, name='verification_page'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('qrreader/', views.qrreader, name='qrreader'),

    path('reserve_parking/', views.reserve_parking, name='reserve_parking'),
    path('cancel_reservation/', views.cancel_reservation, name='cancel_reservation'),  
    path('view_reservation/', views.view_reservation, name='view_reservation'),
    
    path('logs/', views.user_logs, name='user_logs'),
    path('reservation_logs/', views.admin_reservation_logs, name='admin_reservation_logs'),
    
]
