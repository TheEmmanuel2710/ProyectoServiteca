from django.urls import re_path,path
from . import views

urlpatterns = [
    re_path(r'^persona$',views.PersonaList.as_view()),
    re_path(r'^persona/(?P<pk>[0-9]+)$',views.PersonaDetail.as_view()),
    re_path(r'^cliente$',views.ClienteList.as_view()),
    re_path(r'^cliente/(?P<pk>[0-9]+)$',views.ClienteDetail.as_view()),
    # path('producto/<int:proCodigo>',views.ProductoDetail.as_view()),
]
