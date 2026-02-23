from django.http import HttpResponse

def debug_view(request):
    return HttpResponse("Debug View Content")