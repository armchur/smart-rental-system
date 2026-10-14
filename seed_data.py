import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartrental_web.settings')
django.setup()

from rental_app.models import EquipmentCategory, Equipment, Customer

def run_seed():
    print("--- Seeding Sample Customer ---")
    customer, created = Customer.objects.get_or_create(
        phone="08031234567",
        defaults={
            "name": "Musa Ibrahim",
            "email": "musa.ibrahim@example.com",
            "address": "No. 14 Bekaji Estate, Jimeta, Yola, Adamawa State"
        }
    )
    status = "Created" if created else "Exists"
    print(f"[{status}] Customer: {customer.name} ({customer.phone})")
    print("\n>>> All seeding completed 100% successfully! <<<")

if __name__ == "__main__":
    run_seed()
