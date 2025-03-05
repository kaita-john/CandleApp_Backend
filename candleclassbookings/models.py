from django.db import models

class CandleClassBooking(models.Model):
    CLASS_TYPES = (
        ('Online Class', 'Online Class'),
        ('Private In-Person Class', 'Private In-Person Class'),
    )

    fullName = models.CharField(max_length=100)
    phoneNumber = models.CharField(max_length=20)
    email = models.EmailField()
    classType = models.CharField(max_length=50, choices=CLASS_TYPES)
    availableDateTime = models.CharField(max_length=200)  # You might want to use DateTimeField if you want to parse dates
    participants = models.CharField(max_length=100, null=True, blank=True)
    eventType = models.CharField(max_length=100, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    specialRequests = models.TextField(null=True, blank=True)
    amount = models.DecimalField(max_digits=15, default=0.00, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.fullName} - {self.classType} Booking"

    class Meta:
        verbose_name = "Candle Class Booking"
        verbose_name_plural = "Candle Class Bookings"