from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter

from .views import DoctorViewSet, SpecializationViewSet, PublicationViewSet, ConsultationViewSet


router = DefaultRouter()

router.register(r'doctors', DoctorViewSet, basename='doctors')
router.register(r'specializations', SpecializationViewSet, basename='specializations')
router.register(r'publications', PublicationViewSet, basename='publications')
router.register(r'consultations', ConsultationViewSet, basename='consultations')

urlpatterns = [
    path('consultations/<int:start_year>-<int:start_month>-<int:start_day>/<int:end_year>-<int:end_month>-<int:end_day>'
         '/<int:doctor>', ConsultationViewSet.as_view({'get': 'list'})),
    path('auth', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]

urlpatterns += router.urls
