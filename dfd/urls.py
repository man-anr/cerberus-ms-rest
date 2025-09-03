from django.urls import path

from dfd.health import HealthView
from .views import (
    # Users
    UserListCreateView, UserDetailView,
    # Projects
    ProjectListCreateView, ProjectDetailView,
    # Diagrams
    DiagramListCreateView, DiagramDetailView,
    # Components
    ComponentListCreateUnderDiagramView, ComponentDetailUnderDiagramView,
)

urlpatterns = [
    path('health/', HealthView.as_view(), name='health'),

    # Users
    path('users/', UserListCreateView.as_view(), name='user-list-create'),
    path('users/<str:user_key>/', UserDetailView.as_view(), name='user-detail'),

    # Projects
    path('projects/', ProjectListCreateView.as_view(), name='project-list-create'),
    path('projects/<str:project_id>/', ProjectDetailView.as_view(), name='project-detail'),

    # Diagrams under project
    path('projects/<str:project_id>/diagrams/', DiagramListCreateView.as_view(), name='diagram-list-create'),
    path('projects/<str:project_id>/diagrams/<str:diagram_id>/', DiagramDetailView.as_view(), name='diagram-detail'),

    # Components under diagram
    path('projects/<str:project_id>/diagrams/<str:diagram_id>/components/',
         ComponentListCreateUnderDiagramView.as_view(), name='component-list-create'),
    path('projects/<str:project_id>/diagrams/<str:diagram_id>/components/<str:component_id>/',
         ComponentDetailUnderDiagramView.as_view(), name='component-detail'),
]
