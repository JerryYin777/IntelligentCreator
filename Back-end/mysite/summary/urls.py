from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signal_generate', views.signal_generate),
    path('batch_generate', views.batch_generate),
    path('show_generate', views.show_generate),
    path('show_generate_files', views.show_generate_files),
    path('del_file', views.del_file),
    path('upload_file', views.upload_file),
    path('show_all_files', views.show_all_files),
]