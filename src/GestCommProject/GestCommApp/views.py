from django.shortcuts import render
from GestCommApp.models import Article, Client, Devis, Facture
from GestCommApp.serializers import (
    ArticleSerializer, ClientSerializer, DevisSerializer, FactureSerializer)
from GestCommApp.assistant import answer as assistant_answer
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

# Create your views here.


class ClientList(generics.ListCreateAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


class ClientDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


class ArticleList(generics.ListCreateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer


class ArticleDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer


class DevisList(generics.ListCreateAPIView):
    queryset = Devis.objects.prefetch_related('lignes__article')
    serializer_class = DevisSerializer


class DevisDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Devis.objects.prefetch_related('lignes__article')
    serializer_class = DevisSerializer


class FactureList(generics.ListCreateAPIView):
    queryset = Facture.objects.prefetch_related('lignes__article')
    serializer_class = FactureSerializer


class FactureDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Facture.objects.prefetch_related('lignes__article')
    serializer_class = FactureSerializer


class AssistantAsk(APIView):
    """POST /api/assistant/ask {question} — deterministic copilot intents.

    Read-only by design: it answers questions about clients using the same
    ORM the REST API exposes. Write intents (create/update) are deliberately
    absent until a confirmation flow exists.
    """

    def post(self, request):
        question = request.data.get("question", "")
        return Response(assistant_answer(question))
