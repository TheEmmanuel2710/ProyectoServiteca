from django.urls import path
from . import views

urlpatterns = [
    path('persona', views.PersonaList.as_view()),
    path('persona/<int:perIdentificacion>', views.PersonaDetail.as_view()),
    path('cliente', views.ClienteList.as_view()),
    path('cliente/<str:perIdentificacion>', views.ClienteDetail.as_view()),
    path('servicioPrestado', views.ServicioPrestadoList.as_view()),
    path('servicioPrestado/<int:pk>', views.ServicioPrestadoDetail.as_view()),
    path('detalleServicioPrestado/<int:id>', views.DetalleServicioPrestadoList.as_view()),
]
