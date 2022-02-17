from django.urls import path, include
from rest_framework import routers

from broker.views import MessageViewSet, UserViewSet

router = routers.DefaultRouter()
router.register('messages', MessageViewSet)
router.register('users', UserViewSet, 'users')


urlpatterns = [
    path('', include(router.urls)),
]
