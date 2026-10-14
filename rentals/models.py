from django.db import models
from django.utils import timezone


class EquipmentCategory(models.Model):
    """The 8 equipment classes recognized by the VGG16 CNN."""
    code = models.CharField(max_length=50, unique=True, help_text="e.g. generator, chainsaw")
    name = models.CharField(max_length=100, help_text="e.g. Portable Generator")
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Equipment Categories"

    def __str__(self):
        return self.name


class Equipment(models.Model):
    """Physical rental items in stock."""
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('rented', 'Rented Out'),
        ('maintenance', 'Under Maintenance'),
    ]

    category = models.ForeignKey(EquipmentCategory, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=150)
    serial_number = models.CharField(max_length=100, unique=True)
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2, help_text="Daily rental fee in Naira (NGN)")
    caution_fee = models.DecimalField(max_digits=10, decimal_places=2, default=5000.00, help_text="Refundable deposit")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    photo = models.ImageField(upload_to='equipment_photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Equipment Inventory"

    def __str__(self):
        return f"{self.name} ({self.serial_number}) - {self.get_status_display()}"


class Customer(models.Model):
    """Renter profiles."""
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    id_card_number = models.CharField(max_length=50, help_text="NIN or Driver's License or Student ID")
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.phone})"


class Rental(models.Model):
    """Rental transactions / contracts."""
    STATUS_CHOICES = [
        ('active', 'Active (With Renter)'),
        ('returned', 'Returned & Completed'),
        ('overdue', 'Overdue'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='rentals')
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='rentals')
    start_date = models.DateField(default=timezone.now)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(blank=True, null=True)
    daily_rate_applied = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    notes = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        # Auto-compute rental days and total cost
        if not self.daily_rate_applied:
            self.daily_rate_applied = self.equipment.daily_rate
        days = max(1, (self.expected_return_date - self.start_date).days)
        self.total_amount = days * self.daily_rate_applied
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Rental #{self.id} - {self.equipment.name} to {self.customer.full_name}"


class RecognitionLog(models.Model):
    """
    Audit log of every image upload recognized by the VGG16 CNN microservice.
    Fulfills non-functional audit requirements in Chapter 3.
    """
    image = models.ImageField(upload_to='scans/')
    predicted_class = models.CharField(max_length=100)
    confidence = models.FloatField(help_text="Confidence percentage (0-100)")
    accepted = models.BooleanField(help_text="True if confidence >= 65% (acceptance threshold)")
    top3_json = models.TextField(blank=True, help_text="Serialized top-3 predictions and probabilities")
    associated_equipment = models.ForeignKey(Equipment, on_delete=models.SET_NULL, null=True, blank=True)
    scanned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        status_text = "Accepted" if self.accepted else "Flagged (<65%)"
        return f"Scan #{self.id}: {self.predicted_class} ({self.confidence:.1f}%) - {status_text}"
