from django.urls import path, include
from api import views
from rest_framework.routers import DefaultRouter
router = DefaultRouter()

router.register('developer', views.DeveloperViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('developer-login/', views.DeveloperLoginApiView.as_view()),
]
