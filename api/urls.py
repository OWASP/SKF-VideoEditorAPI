from django.urls import path, include
from api import views
from rest_framework.routers import DefaultRouter
router = DefaultRouter()

urlpatterns = [
    ## Example signup
    ## path('signup/', views.UserAccountAPIView.as_view()),

    path("", include(router.urls))
]
