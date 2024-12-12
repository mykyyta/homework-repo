from django.http import HttpResponse

def trainers(request):
    return HttpResponse("Trainers")

def specific_trainer(request, trainer_id):
    return HttpResponse("Specific trainer")

def specific_service(request, trainer_id, service_id):
    return HttpResponse("Specific trainer. Specific service")

def service_booking(request, trainer_id, service_id):
    return HttpResponse("Service booking")