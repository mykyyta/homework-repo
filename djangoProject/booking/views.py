from django.http import HttpResponse

# Create your views here.

def booking_details(request, booking_id):
    return HttpResponse(f"booking details, id: {booking_id}")

def accept_booking(request, booking_id):
    return HttpResponse(f"booking {booking_id} accepted")

def cancel_booking(request, booking_id):
    return HttpResponse(f"booking {booking_id} canceled")
