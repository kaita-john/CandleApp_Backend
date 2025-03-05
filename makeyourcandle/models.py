from django.db import models


from django.db import models

class MakeYourCandle(models.Model):
    # Question 1: Purpose of the candle (multiple options allowed, stored as comma-separated values)
    purpose = models.CharField(max_length=255, help_text="Purpose of the candle (e.g., Baby Shower, Wedding Gift, etc.)")
    # Question 2: Number of candles
    quantity = models.CharField(max_length=50, help_text="Number of candles (e.g., 1-10, 11-20, etc.)")
    # Question 3: Preferred scent
    scent = models.CharField(max_length=100, help_text="Preferred scent (e.g., Vanilla, Mango, etc.)")
    # Question 4: Preferred candle jar color
    jar_color = models.CharField(max_length=100, help_text="Preferred candle jar color (e.g., Frosted Red, Frosted White, etc.)")
    # Question 5: Special labeling or messaging
    special_labeling = models.CharField(max_length=3, help_text="Do you need special labeling? (Yes/No)")
    custom_message = models.CharField(max_length=255, blank=True, null=True, help_text="Custom message for labeling (if applicable)")
    # Question 6: Timeline for delivery
    delivery_timeline = models.CharField(max_length=100, help_text="When do you need the candles by? (e.g., Within a week, 1-2 weeks, etc.)")
    # Question 7: Additional notes or requests
    additional_notes = models.TextField(blank=True, null=True, help_text="Any additional notes or requests")
    # Contact Details
    email = models.EmailField(help_text="Customer's email address")
    phone_number = models.CharField(max_length=20, help_text="Customer's phone number")
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the order was created")
    updated_at = models.DateTimeField(auto_now=True, help_text="Timestamp when the order was last updated")

    def __str__(self):
        return f"Candle Order #{self.id} - {self.email}"

    class Meta:
        verbose_name = "Make Your Candle Order"
        verbose_name_plural = "Make Your Candle Orders"