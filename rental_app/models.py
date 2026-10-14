from datetime import date
from django.db import models


class EquipmentCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Equipment Categories"

    def __str__(self):
        return self.name


class Equipment(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('rented', 'Rented'),
        ('maintenance', 'Under Maintenance'),
    ]

    name = models.CharField(max_length=150)
    category = models.ForeignKey(
        EquipmentCategory, on_delete=models.CASCADE, related_name='equipment'
    )
    serial_number = models.CharField(max_length=100, blank=True, null=True)
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='available'
    )
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"


class Customer(models.Model):
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    registered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.phone}"


class RecognitionLog(models.Model):
    uploaded_image = models.ImageField(upload_to='scans/', blank=True, null=True)
    predicted_class = models.CharField(max_length=100)
    confidence = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.predicted_class} ({self.confidence * 100:.1f}%)"


class Rental(models.Model):
    equipment = models.ForeignKey(
        Equipment, on_delete=models.CASCADE, related_name='rentals'
    )
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name='rentals'
    )
    recognition_log = models.ForeignKey(
        RecognitionLog,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='rentals',
    )
    rental_date = models.DateField(default=date.today)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(blank=True, null=True)
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00
    )
    notes = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # Calculate rental duration and total cost
        if isinstance(self.rental_date, str):
            self.rental_date = date.fromisoformat(self.rental_date)
        if isinstance(self.expected_return_date, str):
            self.expected_return_date = date.fromisoformat(
                self.expected_return_date
            )

        duration = max(1, (self.expected_return_date - self.rental_date).days)
        self.total_amount = duration * self.equipment.daily_rate
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Rental #{self.id}: {self.equipment.name} to {self.customer.name}"
