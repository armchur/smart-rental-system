import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartrental_web.settings')
django.setup()

from rental_app.models import EquipmentCategory, Equipment, Customer

# 1. Categories
categories = [
    'Generator', 'Concrete Mixer', 'Welding Machine', 'Electric Drill',
    'Water Pump', 'Chainsaw', 'Lawn Mower', 'Air Compressor'
]

cat_objs = {}
for name in categories:
    cat, _ = EquipmentCategory.objects.get_or_create(name=name)
    cat_objs[name] = cat
print(f"Categories in DB: {len(cat_objs)}")

# 2. Equipment Units
items = [
    ('Lutian 5.5KVA Petrol Generator', 'Generator', 'GEN-LT-001', 8500.00),
    ('Tiger TG950 Portable Generator', 'Generator', 'GEN-TG-002', 3500.00),
    ('Belle 350L Concrete Mixer', 'Concrete Mixer', 'MIX-BL-101', 12000.00),
    ('Ingco 200A Inverter Welding Machine', 'Welding Machine', 'WLD-ING-201', 5000.00),
    ('Bosch Professional GSB 16 RE Drill', 'Electric Drill', 'DRL-BSH-301', 2500.00),
    ('Honda WT30X 3-Inch Water Pump', 'Water Pump', 'PMP-HN-401', 6500.00),
    ('Stihl MS 382 Petrol Chainsaw', 'Chainsaw', 'CHN-ST-501', 7500.00),
    ('Husqvarna LC 140P Lawn Mower', 'Lawn Mower', 'MOW-HQ-601', 4500.00),
    ('Puma 3HP 100L Air Compressor', 'Air Compressor', 'CMP-PM-701', 7000.00),
]

for name, cat_name, serial, rate in items:
    Equipment.objects.get_or_create(
        name=name,
        defaults={
            'category': cat_objs[cat_name],
            'serial_number': serial,
            'daily_rate': rate,
            'status': 'available',
        }
    )
print(f"Seeded {len(items)} equipment units.")

# 3. Customers
Customer.objects.get_or_create(
    phone='08031234567',
    defaults={'name': 'Musa Ibrahim', 'email': 'musa@example.com', 'address': 'Bekaji, Jimeta, Yola'}
)
Customer.objects.get_or_create(
    phone='08029876543',
    defaults={'name': 'Amina Garba', 'email': 'amina@example.com', 'address': 'MAU Campus, Girei'}
)
print("Seeded customers. All done!")