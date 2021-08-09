from django.contrib import admin
from django.urls import path
from django.conf.urls import include


def home(request):
    return HttpResponse


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('simpleQuestionGenerator.urls')),
]
