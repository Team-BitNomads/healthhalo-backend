from django.urls import path
from .views import (
    CircleListCreateView,
    CircleDetailView,
    ContributionView,
    ClaimCreateView,
    MembershipListView
)

urlpatterns = [
    path('', CircleListCreateView.as_view(), name='circle-list'),
    path('<int:pk>/', CircleDetailView.as_view(), name='circle-detail'),
    path('<int:circle_id>/members/', MembershipListView.as_view(), name='circle-members'),
    path('<int:circle_id>/contribute/', ContributionView.as_view(), name='contribute'),
    path('<int:circle_id>/claim/', ClaimCreateView.as_view(), name='create-claim'),
]
