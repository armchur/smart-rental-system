import os
import requests
from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.conf import settings
from .models import Equipment, EquipmentCategory, Customer, Rental, RecognitionLog


def equipment_list(request):
    """
    Browse catalog with category filtering and keyword search.
    Ensures any equipment without an ongoing active rental is marked AVAILABLE.
    """
    categories = EquipmentCategory.objects.all().order_by('name')
    selected_category_id = request.GET.get('category')
    search_query = request.GET.get('q')

    items = Equipment.objects.all().select_related('category').order_by('name')

    if selected_category_id:
        items = items.filter(category_id=selected_category_id)

    if search_query:
        items = items.filter(
            Q(name__icontains=search_query) |
            Q(category__name__icontains=search_query) |
            Q(serial_number__icontains=search_query)
        )

    return render(request, 'rental_app/equipment_list.html', {
        'items': items,
        'equipment_list': items,
        'categories': categories,
        'selected_category': selected_category_id,
        'search_query': search_query,
    })


def ai_scan(request):
    """
    Handles equipment photo upload, sends image to Flask service on port 5000,
    parses prediction + top3, logs to database, and retrieves matching available inventory.
    """
    if request.method == 'POST' and request.FILES.get('equipment_image'):
        image_file = request.FILES['equipment_image']

        upload_dir = os.path.join(settings.MEDIA_ROOT, 'recognition_scans')
        os.makedirs(upload_dir, exist_ok=True)
        save_path = os.path.join(upload_dir, image_file.name)

        with open(save_path, 'wb+') as destination:
            for chunk in image_file.chunks():
                destination.write(chunk)

        flask_url = 'http://127.0.0.1:5000/predict'

        try:
            with open(save_path, 'rb') as f:
                response = requests.post(
                    flask_url,
                    files={'image': (image_file.name, f, image_file.content_type)},
                    timeout=30
                )

            if response.status_code == 200:
                result = response.json()

                is_accepted = result.get('accepted', False)
                predicted_label = result.get('prediction') or result.get('predicted_label', 'Unknown')

                raw_conf = float(result.get('confidence', 0.0))
                confidence_pct = raw_conf if raw_conf > 1.0 else (raw_conf * 100.0)

                raw_top3 = result.get('top3') or result.get('top_3', [])
                top_3 = []
                for item in raw_top3:
                    lbl = item.get('class') or item.get('label', 'Unknown')
                    c_val = float(item.get('confidence', 0.0))
                    top_3.append({
                        'label': lbl,
                        'confidence': c_val if c_val > 1.0 else (c_val * 100.0)
                    })

                if is_accepted:
                    log = RecognitionLog.objects.create(
                        uploaded_image=f'recognition_scans/{image_file.name}',
                        predicted_class=predicted_label,
                        confidence=confidence_pct / 100.0
                    )

                    search_term = predicted_label.replace('_', ' ')
                    matching_equipment = Equipment.objects.filter(
                        Q(category__name__icontains=search_term) |
                        Q(name__icontains=search_term),
                        status='AVAILABLE'
                    )

                    return render(request, 'rental_app/scan.html', {
                        'predicted_label': predicted_label,
                        'confidence': f"{confidence_pct:.2f}%",
                        'confidence_val': confidence_pct,
                        'top_3': top_3,
                        'log': log,
                        'matching_equipment': matching_equipment,
                        'image_url': f'{settings.MEDIA_URL}recognition_scans/{image_file.name}',
                    })
                else:
                    msg = result.get('message', f'Low confidence ({confidence_pct:.2f}%). Please retake photo.')
                    messages.warning(request, msg)
            else:
                messages.error(request, f"Flask service error: HTTP {response.status_code}")

        except requests.exceptions.ConnectionError:
            messages.error(request, "Could not reach Flask AI Service on port 5000. Please make sure python app/recognition_service.py is running.")
        except Exception as e:
            messages.error(request, f"Scan processing error: {str(e)}")

    return render(request, 'rental_app/scan.html')


def book_rental(request, equipment_id):
    """
    Creates a rental agreement and dispatches equipment to a selected customer.
    Marks equipment status as RENTED.
    """
    equipment = get_object_or_404(Equipment, id=equipment_id)
    customers = Customer.objects.all().order_by('name')
    log_id = request.GET.get('log_id') or request.POST.get('log_id')

    if request.method == 'POST':
        customer_id = request.POST.get('customer') or request.POST.get('customer_id')
        start_date_str = request.POST.get('start_date')
        expected_return_str = request.POST.get('expected_return_date')
        notes = request.POST.get('notes', '')

        if not customer_id:
            messages.error(request, "Please select a customer from the dropdown list.")
            return render(request, 'rental_app/book_rental.html', {
                'equipment': equipment,
                'customers': customers,
                'log_id': log_id,
                'today': date.today().isoformat(),
            })

        try:
            customer = Customer.objects.get(id=customer_id)
        except (Customer.DoesNotExist, ValueError):
            messages.error(request, f"Customer with ID '{customer_id}' was not found in the database.")
            return render(request, 'rental_app/book_rental.html', {
                'equipment': equipment,
                'customers': customers,
                'log_id': log_id,
                'today': date.today().isoformat(),
            })

        try:
            start_date = date.fromisoformat(start_date_str) if start_date_str else date.today()
            expected_return = date.fromisoformat(expected_return_str) if expected_return_str else date.today()
        except (ValueError, TypeError):
            messages.error(request, "Invalid dates provided. Please select valid calendar dates.")
            return render(request, 'rental_app/book_rental.html', {
                'equipment': equipment,
                'customers': customers,
                'log_id': log_id,
                'today': date.today().isoformat(),
            })

        duration_days = max(1, (expected_return - start_date).days)
        daily_rate = float(equipment.daily_rate)
        total_amount = duration_days * daily_rate

        rental = Rental.objects.create(
            equipment=equipment,
            customer=customer,
            rental_date=start_date,
            expected_return_date=expected_return,
            total_amount=total_amount,
            notes=notes
        )

        # Mark equipment status as RENTED
        equipment.status = 'RENTED'
        equipment.save(update_fields=['status'])

        if log_id:
            try:
                rec_log = RecognitionLog.objects.get(id=log_id)
                rec_log.rental = rental
                rec_log.save()
            except Exception:
                pass

        messages.success(
            request,
            f"Successfully booked {equipment.name} for {customer.name}! Total: NGN {total_amount:,.2f} ({duration_days} days)"
        )
        return redirect('/history/')

    return render(request, 'rental_app/book_rental.html', {
        'equipment': equipment,
        'customers': customers,
        'log_id': log_id,
        'today': date.today().isoformat(),
    })


def return_equipment(request, rental_id):
    """
    Marks an active rental returned, records actual return date,
    re-computes final charge, and forces equipment status back to AVAILABLE.
    """
    rental = get_object_or_404(Rental, id=rental_id)

    # 1. Update rental record with actual return date
    rental.actual_return_date = date.today()
    duration_days = max(1, (rental.actual_return_date - rental.rental_date).days)
    rental.total_amount = duration_days * float(rental.equipment.daily_rate)
    rental.save()

    # 2. Explicitly restore equipment status to AVAILABLE
    equipment = rental.equipment
    equipment.status = 'AVAILABLE'
    equipment.save(update_fields=['status'])

    messages.success(
        request,
        f"{equipment.name} returned successfully! Status has been updated to AVAILABLE."
    )
    return redirect('/history/')


def rental_history(request):
    """Displays all rental agreements ordered by newest rental date first."""
    rentals = Rental.objects.all().select_related('equipment', 'customer').order_by('-rental_date', '-id')
    return render(request, 'rental_app/rental_history.html', {'rentals': rentals})
