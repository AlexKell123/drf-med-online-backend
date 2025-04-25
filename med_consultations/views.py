import datetime
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .permissions import IsOwnerOrReadOnly
from .serializers import AllDoctorsSerializer, OneDoctorSerializer, AllSpecializationsSerializer, \
    OneSpecializationSerializer, PublicationSerializer, AllConsultationSerializer, SpecialWorkTimeSerializer, \
    WorkTimeSerializer, OneConsultationSerializer
from .models import Doctor, Specialization, Publication, WorkTime, Consultation, SpecialWorkTime
from .validators import ConsultationValidator


consultation_validator = ConsultationValidator()

class SpecializationViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = Specialization.objects.all()
        serializer = AllSpecializationsSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Specialization.objects.all()
        specialization = get_object_or_404(queryset, pk=pk)
        serializer = OneSpecializationSerializer(specialization)
        return Response(serializer.data)

class DoctorViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = Doctor.objects.all()
        serializer = AllDoctorsSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Doctor.objects.all()
        doctor = get_object_or_404(queryset, pk=pk)
        serializer = OneDoctorSerializer(doctor)
        return Response(serializer.data)

class PublicationViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = Publication.objects.all()
        serializer = PublicationSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Publication.objects.all()
        publication = get_object_or_404(queryset, pk=pk)
        serializer = PublicationSerializer(publication)
        return Response(serializer.data)

class ConsultationViewSet(viewsets.ViewSet):
    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsOwnerOrReadOnly]
        return [permission() for permission in permission_classes]

    def list(self, request, *args, **kwargs):
        try:
            doctor_id = self.kwargs['doctor']
            start_date = datetime.date(self.kwargs['start_year'], self.kwargs['start_month'], self.kwargs['start_day'])
            end_date = datetime.date(self.kwargs['end_year'], self.kwargs['end_month'], self.kwargs['end_day'])
        except:
            return Response({'error': 'incorrect dates or doctor_id'})

        queryset = Consultation.objects.filter(doctor=doctor_id, datetime__range=[start_date, end_date])
        serializer = AllConsultationSerializer(queryset, many=True)
        consultations = serializer.data

        queryset = SpecialWorkTime.objects.filter(doctor=doctor_id, date__range=[start_date, end_date])
        serializer = SpecialWorkTimeSerializer(queryset, many=True)
        special_work_time = serializer.data

        queryset = WorkTime.objects.filter(doctor=doctor_id)
        serializer = WorkTimeSerializer(queryset, many=True)
        work_time = serializer.data

        return Response({'doctor_id': doctor_id, 'consultations': consultations,
                         'special_work_time': special_work_time, 'work_time': work_time})

    def retrieve(self, request, pk=None):
        queryset = Consultation.objects.all()
        consultation = get_object_or_404(queryset, pk=pk)
        serializer = OneConsultationSerializer(consultation)
        return Response(serializer.data)

    def create(self, request):
        serializer = OneConsultationSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        consultation_validator.check_errors(serializer.validated_data['datetime'], serializer.validated_data['doctor'])
        serializer.save()
        return Response({'Consultation created': serializer.data})

    def update(self, request, *args, **kwargs):
        pk = kwargs.get("pk", None)
        if not pk:
            return Response({"error": "Method PUT not allowed"})
        try:
            instance = Consultation.objects.get(pk=pk)
        except:
            return Response({"error": "Object does not exists"})

        serializer = OneConsultationSerializer(data=request.data, instance=instance, context={'request': request})
        serializer.is_valid(raise_exception=True)
        consultation_validator.check_errors(serializer.validated_data['datetime'], serializer.validated_data['doctor'])
        serializer.save()
        return Response({'Consultation updated': serializer.data})

    def destroy(self, request, *args, **kwargs):
        pk = kwargs.get("pk", None)
        if not pk:
            return Response({"error": "Method DELETE not allowed"})
        try:
            Consultation.objects.filter(pk=pk).delete()
        except:
            return Response({"error": "Object does not exists"})

        return Response({"Consultation deleted": str(pk)})
