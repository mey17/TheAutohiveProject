from base64 import decode
from django.shortcuts import render, redirect
from django.db import transaction
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegisterForm
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from PIL import Image
from django.core.mail import EmailMessage
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import login
from .models import EmailVerification
from user.forms import ProfileUpdateForm
from django.http import JsonResponse
from .models import ParkingPlace, Reservation, Slot
from datetime import datetime, timedelta
from django.utils.timezone import now, timedelta
from django.shortcuts import redirect, render
from django.contrib.auth import login
from django.core.mail import EmailMessage
from .models import EmailVerification, ReservationLog
from .forms import UserRegisterForm, VerificationForm
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
import json
from django.utils import timezone
from .forms import ParkingPlaceForm as ParkingLotForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from .forms import UserRegisterForm, VerificationForm
from .models import EmailVerification
from .models import ParkingPlace, Slot, Reservation, ReservationLog
import random
from django.utils.translation import gettext as _
from .models import ParkingPlace, Slot, Reservation
from .forms import ParkingPlaceForm
from django.utils.timezone import localtime, make_aware
from pytz import timezone
import requests  

def index(request):
    return render(request, 'user/index.html', {'title': 'index'})

def anonymous_required(view_function):
    """
    Decorator to restrict access to a view for logged-in users.
    Redirects logged-in users to a specified page.
    """
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('index')  
        return view_function(request, *args, **kwargs)
    return wrapper

def Login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome {username}!')
            return redirect('index')
        else:
            messages.info(request, 'Account does not exist. Please sign up.')
    form = AuthenticationForm()
    return render(request, 'user/login.html', {'form': form, 'title': 'log in'})

@login_required
def account_details(request):
    profile = request.user.profile
    return render(request, 'user/account_details.html', {
        'profile': profile,
        'title': 'Account Details',
    })

def is_admin_or_superuser(user):
    return user.is_superuser or user.is_staff


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from pyzbar.pyzbar import decode
from PIL import Image
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from PIL import Image
import cv2
import numpy as np

from .models import ParkingPlace
from django.contrib.auth.models import User
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import websocket
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
@csrf_exempt
@staff_member_required
def qrreader(request):
    """
    Scans a QR code, verifies the user, and opens the barrier if valid.
    """
    if request.method == 'POST':
        frame = request.FILES.get('frame')  
        parking_place_id = request.POST.get('parking_place')
        scan_type = request.POST.get('scan_type')

        if not frame:
            return JsonResponse({'status': 'error', 'message': 'No frame provided.'})
        if not parking_place_id:
            return JsonResponse({'status': 'error', 'message': 'No parking place selected.'})
        if not scan_type:
            return JsonResponse({'status': 'error', 'message': 'No scan type selected.'})

        try:
            parking_place = ParkingPlace.objects.get(id=parking_place_id)
        except ParkingPlace.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Invalid parking place selected.'})

        try:
           
            image = Image.open(frame)
            image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

            detector = cv2.QRCodeDetector()

    
            data, points, _ = detector.detectAndDecode(image)

            if data:
               
                username = data.split("\n")[0].split(": ")[1] 
                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    return JsonResponse({'status': 'error', 'message': 'Invalid QR code. User does not exist.'})

                reservation = Reservation.objects.filter(
                    user=user,
                    parking_lot=parking_place,
                    is_active=True
                ).first()

                if not reservation:
                    return JsonResponse({'status': 'error', 'message': 'No active reservation found for this user at the selected parking place.'})

                action = "Entering" if scan_type == "entering" else "Exiting"
                ReservationLog.objects.create(
                    action=action,
                    user=user,
                    parking_lot=parking_place,
                    slot=reservation.slot,
                    timestamp=now()
                )

           
                if scan_type == "exiting":
                    reservation.is_active = False
                    reservation.slot.is_reserved = False
                    reservation.slot.save()
                    reservation.save()
                    ESP8266_HTTP_URL = "http://192.168.152.67/move_servo"  
                    try:
                        response = requests.post(ESP8266_HTTP_URL, data=user.username)  
                        if response.status_code == 200:
                            print(f"Barrier opened successfully for {user.username}.")
                            return JsonResponse({'status': 'success', 'message': f'Barrier opened for {user.username}.'})
                        else:
                            print(f"Failed to open barrier. Status code: {response.status_code}, Response: {response.text}")
                            return JsonResponse({'status': 'error', 'message': 'Failed to open barrier.'})
                    except requests.exceptions.RequestException as e:
                        print(f"Error opening barrier: {e}")
                        return JsonResponse({'status': 'error', 'message': 'Failed to connect to the barrier system. Please try again later.'})

                
                if scan_type == "entering":
                    ESP8266_HTTP_URL = "http://192.168.152.67/move_servo" 
                    try:
                        response = requests.post(ESP8266_HTTP_URL, data=user.username)  
                        if response.status_code == 200:
                            print(f"Barrier opened successfully for {user.username}.")
                            return JsonResponse({'status': 'success', 'message': f'Barrier opened for {user.username}.'})
                        else:
                            print(f"Failed to open barrier. Status code: {response.status_code}, Response: {response.text}")
                            return JsonResponse({'status': 'error', 'message': 'Failed to open barrier.'})
                    except requests.exceptions.RequestException as e:
                        print(f"Error opening barrier: {e}")
                        return JsonResponse({'status': 'error', 'message': 'Failed to connect to the barrier system. Please try again later.'})

                return JsonResponse({'status': 'success', 'message': f'{action} action logged for {user.username}.'})

            else:
                return JsonResponse({'status': 'error', 'message': 'No QR code found in the frame.'})
        except Exception as e:
            print(f"Error in qrreader: {e}")  
            return JsonResponse({'status': 'error', 'message': f'Error processing frame: {str(e)}'})

    parking_places = ParkingPlace.objects.all()
    return render(request, 'user/qrreader.html', {'parking_places': parking_places})
@csrf_exempt
@staff_member_required
def open_barrier(request):
    """
    Opens the barrier without QR code verification.
    """
    # if request.method == 'POST':
    #     try:
    #         # ESP8266 HTTP server URL
    #         ESP8266_HTTP_URL = "http://192.168.10.67/move_servo"  # Replace with the actual IP address of your ESP8266
            
    #         # Send the HTTP POST request to the ESP8266
    #         response = requests.post(ESP8266_HTTP_URL, data="0")  # Trigger the barrier to open
    #         if response.status_code == 200:
    #             print("Barrier opened successfully.")
    #             return JsonResponse({'status': 'success', 'message': 'Barrier opened successfully.'})
    #         else:
    #             print(f"Failed to open barrier. Status code: {response.status_code}, Response: {response.text}")
    #             return JsonResponse({'status': 'error', 'message': 'Failed to open barrier.'})
    #     except requests.exceptions.RequestException as e:
    #         print(f"Error opening barrier: {e}")
    #         return JsonResponse({'status': 'error', 'message': f'Error opening barrier: {str(e)}'})
    # return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

@anonymous_required
def verification_page(request):

    user_data = request.session.get('unverified_user_data')
    verification_code = request.session.get('verification_code')
    code_timestamp = request.session.get('verification_code_timestamp')
    if code_timestamp:
        expiration_time = datetime.fromisoformat(code_timestamp) + timedelta(minutes=2)
        if now() > expiration_time:
            del request.session['unverified_user_data']
            del request.session['verification_code']
            del request.session['verification_code_timestamp']
            messages.error(request, 'Your verification code has expired. Please register again.')
            return redirect('register')

    if not user_data or not verification_code:
        return redirect('register') 

    if request.method == "POST":
        form = VerificationForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['verification_code']

            if code == verification_code:
           
                user = User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    password=user_data['password'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name']
                )
                user.profile.phone_no = user_data['phone_no']  
                user.profile.save()

            
                del request.session['unverified_user_data']
                del request.session['verification_code']

                
                login(request, user)

                messages.success(request, 'Your email has been verified successfully!')
                return redirect('index')  
            else:
                form.add_error('verification_code', 'Invalid verification code.')
    else:
        form = VerificationForm()

    return render(request, 'user/verification_page.html', {'form': form})

@login_required
def is_verified(request):
    if not request.user.emailverification.is_verified:
        messages.warning(request, 'Please verify your email address to continue.')
        return redirect('verification_page')
    return redirect('account')



@anonymous_required
def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

      
            verification = EmailVerification.objects.create(
                user=user,
                created_at=now(),
            )

           
            verification_code = str(random.randint(1000, 9999))
            verification.verification_code = verification_code
            verification.save()

            
            email_subject = 'Your Verification Code'
            email_message = render_to_string(
                'user/Email.html',
                {'username': user.username, 'code': verification_code}
            )
            email = EmailMessage(
                subject=email_subject,
                body=email_message,
                from_email='your-email@gmail.com',  
                to=[user.email],
            )
            email.content_subtype = 'html'
            email.send()

            
            request.session['verification_id'] = verification.id
            request.session['verification_code_timestamp'] = now().isoformat()

            return redirect('verification_page') 
    else:
        form = UserRegisterForm()

    return render(request, 'user/register.html', {'form': form})




@anonymous_required
def verification_page(request):
    
    verification_id = request.session.get('verification_id')
    if not verification_id:
        return redirect('register') 

    try:
        verification = EmailVerification.objects.get(id=verification_id)
    except EmailVerification.DoesNotExist:
        return redirect('register')  

  
    expiration_time = verification.created_at + timedelta(minutes=2) 
    if now() > expiration_time:
        verification.delete()  
        return render(request, 'user/verification_expired.html')  

    if request.method == "POST":
        form = VerificationForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['verification_code']

            if verification.verification_code == code:
                verification.is_verified = True
                verification.save()

               
                login(request, verification.user)

               
                del request.session['verification_id']

                
                return redirect('index')

            else:
                form.add_error('verification_code', 'Invalid verification code.')
    else:
        form = VerificationForm()

    return render(request, 'user/verification_page.html', {'form': form})



@login_required
def edit_profile(request):
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect("account")  
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, "user/edit_profile.html", {"form": form})



@login_required
def parking_reservation(request):
    today = now().date()
    max_date = today + timedelta(days=7)

    parking_places = ParkingPlace.objects.filter(is_active=True)
    reserved_slots = Reservation.objects.filter(user=request.user, date__gte=today, is_active=True)

    for place in parking_places:
        reserved_slots_in_place = Reservation.objects.filter(parking_lot=place, is_active=True)
        reserved_slot_ids = reserved_slots_in_place.values_list('slot_id', flat=True)
        available_slots_count = place.max_slots - len(reserved_slot_ids)
        place.available_slots_count = available_slots_count  # Add as a custom attribute

    
    logs = ReservationLog.objects.filter(user=request.user).order_by('-timestamp')

    return render(request, 'user/letspark.html', {
        'parking_places': parking_places,
        'reserved_slots': reserved_slots,
        'today': today,
        'max_date': max_date,
        'logs': logs  
    })

@login_required
def get_available_slots(request, place_id, date):
    parking_place = get_object_or_404(ParkingPlace, id=place_id)
    selected_date = datetime.strptime(date, "%Y-%m-%d").date()
    
    reservations = Reservation.objects.filter(parking_place=parking_place, date=selected_date, is_active=True)

    available_slots = []
    for hour in range(9, 24):  
        if not reservations.filter(start_time=hour).exists():
            available_slots.append(hour)

    return JsonResponse({'available_slots': available_slots})


@login_required
def view_parking_place(request, place_id):

    parking_place = get_object_or_404(ParkingPlace, id=place_id)

    slots = parking_place.slots.all()

    now = localtime(timezone('Asia/Yerevan').localize(datetime.now()))

    expired_reservations = Reservation.objects.filter(end_time__lte=now, is_active=True)
    for res in expired_reservations:
        res.cancel() 


    active_reservations = Reservation.objects.filter(parking_lot=parking_place, is_active=True)
    reserved_slots = active_reservations.values_list('slot_id', flat=True)

 
    available_slots = slots.exclude(id__in=reserved_slots)

    parking_full = available_slots.count() == 0


    user_existing_reservation = active_reservations.filter(user=request.user).first()

    
    if request.method == 'POST':
        slot_id = request.POST.get('slot_id')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')

     
        if not slot_id or not start_time or not end_time:
            messages.error(request, "All fields are required.")
            return redirect('view_parking_place', place_id=place_id)

  
        start_time = make_aware(datetime.strptime(start_time, "%Y-%m-%dT%H:%M"), timezone('Asia/Yerevan'))
        end_time = make_aware(datetime.strptime(end_time, "%Y-%m-%dT%H:%M"), timezone('Asia/Yerevan'))

    
        if not (now.date() <= start_time.date() <= now.date() + timedelta(days=7)):
            messages.error(request, "Reservations can only be made within the next 7 days.")
            return redirect('view_parking_place', place_id=place_id)

        if end_time - start_time > timedelta(hours=12):
            messages.error(request, "Reservations cannot exceed 12 hours.")
            return redirect('view_parking_place', place_id=place_id)

       
        if int(slot_id) in reserved_slots:
            messages.error(request, "This slot is already reserved.")
            return redirect('view_parking_place', place_id=place_id)

        
        slot = get_object_or_404(Slot, id=slot_id)
        if slot.is_reserved:
            messages.error(request, "This slot is already reserved.")
            return redirect('view_parking_place', place_id=place_id)

        slot.is_reserved = True
        slot.save()

        parking_place.reserved_slots += 1
        parking_place.save()

        Reservation.objects.create(
            user=request.user,
            parking_lot=parking_place,
            slot=slot,
            date=start_time.date(),
            start_time=start_time,
            end_time=end_time,
            is_active=True
        )

       
        messages.success(request, "Reservation successful!")
        return redirect('view_parking_place', place_id=place_id)


    return render(request, 'user/view_parking_place.html', {
        'parking_place': parking_place,
        'slots': slots,
        'reserved_slots': reserved_slots,
        'available_slots': available_slots,
        'parking_full': parking_full,
        'active_reservation': user_existing_reservation,
    })


@login_required
def reserve_parking(request):
    if request.method == 'POST':
        try:
            slot_id = request.POST.get('slot_id')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')

            if not all([slot_id, start_time, end_time]):
                return JsonResponse({'error': 'Missing required fields!'}, status=400)

         
            start_time = make_aware(datetime.strptime(start_time, "%Y-%m-%dT%H:%M"))
            end_time = make_aware(datetime.strptime(end_time, "%Y-%m-%dT%H:%M"))

            if not (now().date() <= start_time.date() <= now().date() + timedelta(days=7)):
                return JsonResponse({'error': 'Reservations can only be made within the next 7 days!'}, status=400)

            existing_reservation = Reservation.objects.filter(
                user=request.user, is_active=True, end_time__gte=now()
            ).exists()
            if existing_reservation:
                return JsonResponse({'error': 'You already have an active reservation!'}, status=400)

            slot = get_object_or_404(Slot, id=slot_id)

            if slot.is_reserved:
                return JsonResponse({'error': 'This slot is already reserved!'}, status=400)

          
            slot.is_reserved = True
            slot.save()

            parking_lot = slot.parking_place
            parking_lot.reserved_slots += 1
            parking_lot.save()

            reservation = Reservation.objects.create(
                user=request.user,
                parking_lot=parking_lot,
                slot=slot,
                date=start_time.date(),
                start_time=start_time,
                end_time=end_time,
                is_active=True
            )

       
            ReservationLog.objects.create(
                action="Reservation Made",
                user=request.user,
                parking_lot=parking_lot,
                slot=slot,
                start_time=start_time,
                end_time=end_time
            )

            return redirect('user_logs')

        except Exception as e:
            return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def view_reservation(request):
    reservation = Reservation.objects.filter(user=request.user, is_active=True).first()
    return render(request, 'user/view_reservation.html', {'reservation': reservation})
@login_required
def cancel_reservation(request):
    if request.method == "POST":
 
        reservation = Reservation.objects.filter(user=request.user, is_active=True).first()

        if reservation:
           
            reservation.is_active = False  
            reservation.save()

           
            reservation.slot.is_reserved = False  
            reservation.slot.save()


            reservation.parking_lot.reserved_slots -= 1
            reservation.parking_lot.save()

            ReservationLog.objects.create(
                action="Reservation Canceled",
                user=request.user,
                parking_lot=reservation.parking_lot,
                slot=reservation.slot,
                timestamp=now()
            )

            messages.success(request, "Your reservation has been canceled successfully.")
        else:
            messages.error(request, "You have no active reservation to cancel.")
        
        return redirect('parking_reservation')  
    
    return redirect('view_reservation') 




@login_required
def admin_reservation_logs(request):
    if not request.user.is_staff:
        return redirect('index')
    
    reservations = Reservation.objects.all().order_by('-date', '-start_time')
    return render(request, 'admin/reservation_logs.html', {'reservations': reservations})


@staff_member_required
def add_parking_place(request):
    if request.method == 'POST':
        form = ParkingPlaceForm(request.POST)
        if form.is_valid():
          
            parking_place = form.save()

           
            with transaction.atomic():
                for i in range(1, parking_place.max_slots + 1):
                    Slot.objects.create(
                        parking_place=parking_place,
                        slot_number=i,
                        is_reserved=False  
                    )
            
            return redirect('admin:user_parkingplace_changelist')
    else:
        form = ParkingLotForm()

    return render(request, 'user/add_parking_place.html', {'form': form})


@staff_member_required
def reservation_logs(request):
    logs = ReservationLog.objects.all().order_by('-timestamp')
    return render(request, 'user/reservation_logs.html', {'logs': logs})


def about(request):
    
    return render(request, 'user/about.html')



@login_required
def user_logs(request):
    logs = ReservationLog.objects.filter(user=request.user).order_by('-timestamp')[:20]
    return render(request, 'user/logs.html', {'logs': logs})


from django.shortcuts import render

def custom_404_view(request, exception):
    """
    Custom 404 error page for anonymous users.
    """
    return render(request, 'user/404.html', status=404)

