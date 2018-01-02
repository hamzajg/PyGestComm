from django.shortcuts import render
from GestCommApp.models import Client
from GestCommApp.serializers import ClientSerializer
from rest_framework import generics

# Create your views here.

class ClientList(generics.ListCreateAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer