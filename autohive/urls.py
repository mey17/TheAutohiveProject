from django.contrib import admin
from django.urls import path, include
from user import views as user_view
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.conf.urls import handler404
from user import views as user_views

# Custom error handlers
handler404 = user_views.custom_404_view
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', user_view.index, name='index'),
    path('login/', user_view.Login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', user_view.register, name='register'),
    path('account/', user_view.account_details, name='account'),
    path('qrreader/', user_view.qrreader, name='qrreader'),
    path('add_parking_place/', user_view.add_parking_place, name='add_parking_place'),
    path('letspark/', user_view.parking_reservation, name='parking_reservation'),
    path('cancel_reservation/', user_view.cancel_reservation, name='cancel_reservation'),
    path('verify-email/', user_view.verification_page, name='verification_page'),
    path('edit-profile/', user_view.edit_profile, name='edit_profile'),
    path('reserve_parking/', user_view.reserve_parking, name='reserve_parking'),
    path('view_parking_place/<int:place_id>/', user_view.view_parking_place, name='view_parking_place'),
    path('reservation_logs/', user_view.reservation_logs, name='reservation_logs'),
    path('about/', user_view.about, name='about'),
    path('logs/', user_view.user_logs, name='user_logs'),
    path('view_reservation/', user_view.view_reservation, name='view_reservation'),
    path('cancel_reservation/', user_view.cancel_reservation, name='cancel_reservation'),
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)