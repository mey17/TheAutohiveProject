from django.db import models
from django.contrib.auth.models import User
import qrcode
from io import BytesIO
from django.core.files import File
from datetime import datetime
import hashlib
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import datetime, timedelta
class Profile(models.Model):
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    qr_code = models.ImageField(upload_to='qr_codes', blank=True)
    qr_secret = models.CharField(max_length=64, blank=True)

    def generate_qr_secret(self):
        
        current_date = datetime.now().strftime('%Y-%m-%d')  
        secret = f"{self.user.username}{current_date}"
        return hashlib.sha256(secret.encode()).hexdigest()

    def save(self, *args, **kwargs):
       
        self.qr_secret = self.generate_qr_secret()

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr_data = f"Username: {self.user.username}\nEmail: {self.user.email}\nSecret: {self.qr_secret}"
        qr.add_data(qr_data)
        qr.make(fit=True)

        img = qr.make_image(fill='black', back_color='white')
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        self.qr_code.save(f'{self.user.username}_qr.png', File(buffer), save=False)

        super().save(*args, **kwargs)



class ParkingPlace(models.Model):
    name = models.CharField(max_length=255, unique=True)
    unique_id = models.CharField(max_length=100, unique=True)
    address = models.TextField()
    max_slots = models.IntegerField()
    reserved_slots = models.IntegerField(default=0)
    unavailable_days = models.JSONField(default=list)  # Stores an array of unavailable days
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    @property
    def available_slots(self):
        return self.max_slots - self.reserved_slots


class Slot(models.Model):
    parking_place = models.ForeignKey(ParkingPlace, related_name='slots', on_delete=models.CASCADE)
    slot_number = models.IntegerField()
    is_reserved = models.BooleanField(default=False)

    def __str__(self):
        return f"Slot {self.slot_number} at {self.parking_place.name}"




class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    parking_lot = models.ForeignKey(ParkingPlace, on_delete=models.CASCADE, related_name='reservations')
    slot = models.ForeignKey(Slot, on_delete=models.CASCADE, related_name='reservations')  # Add this line
    date = models.DateField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    reserved_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)


    def __str__(self):
        return f"Reservation for {self.user.username} at {self.parking_lot.name} on {self.date}"

    @property
    def is_expired(self):
        return datetime.now() > self.end_time and self.is_active

    def get_expiry_time(self):
        return self.end_time

    def cancel(self):
        """Cancel the reservation and make the slot available again."""
        self.is_active = False
        self.slot.is_reserved = False  
        self.slot.save() 
        self.save()

    @classmethod
    def active_reservations(cls, user):
        return cls.objects.filter(user=user, is_active=True, end_time__gte=datetime.now())

    @classmethod
    def expired_reservations(cls, user):
        return cls.objects.filter(user=user, is_active=True, end_time__lt=datetime.now())



class EmailVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    verification_code = models.CharField(max_length=4)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return f"Verification for {self.user.username}"
    

class ReservationLog(models.Model):
    action = models.CharField(max_length=255)  
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    parking_lot = models.ForeignKey(ParkingPlace, on_delete=models.CASCADE, null=True, blank=True) 
    slot = models.ForeignKey(Slot, on_delete=models.CASCADE, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)  
    qr_content = models.TextField(null=True, blank=True)  
    start_time = models.DateTimeField(null=True, blank=True)  
    end_time = models.DateTimeField(null=True, blank=True)  

    def __str__(self):
        return f"{self.action} by {self.user.username} on {self.timestamp}"
