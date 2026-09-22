from django.urls import path

from . import views


app_name = "epis"


urlpatterns = [
    path("",views.painel,name="painel"),

    path("funcionarios/",views.funcionarios,name="funcionarios"),
    path("funcionarios/novo/",views.funcionario_novo,name="funcionario_novo"),
    path("funcionarios/<int:pk>/editar/",views.funcionario_editar,name="funcionario_editar"),
    path("funcionarios/<int:pk>/alternar/",views.funcionario_alternar,name="funcionario_alternar"),
    path("funcionarios/<int:pk>/excluir/", views.funcionario_excluir, name="funcionario_excluir"),

    path("epis/", views.epis_lista, name="epis"),
    path("epis/novo/", views.epi_novo, name="epi_novo"),
    path("epis/<int:pk>/editar/", views.epi_editar, name="epi_editar"),
    path("epis/<int:pk>/alternar/", views.epi_alternar, name="epi_alternar"),

    path("entregas/",views.entregas_lista,name="entregas"),
    path("entregas/nova/",views.entrega_nova,name="entrega_nova"),
    path("epis/<int:pk>/excluir/",views.epi_excluir,name="epi_excluir"),

    path("estoque/",views.estoque,name="estoque"),
]