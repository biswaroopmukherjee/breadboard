from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from rest_framework import routers
from api import views


router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'userprofiles', views.UserProfileViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'images', views.ImageViewSet)
router.register(r'runs', views.RunViewSet)
router.register(r'cameras', views.CameraViewSet)
router.register(r'datasets', views.DatasetViewSet)
router.register(r'projects', views.ProjectViewSet)
router.register(r'labs', views.LabViewSet)


urlpatterns = [
    # path('admin/', admin.site.urls),
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
