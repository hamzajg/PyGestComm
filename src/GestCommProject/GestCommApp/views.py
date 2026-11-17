from django.db import transaction
from django.http import Http404
from django.shortcuts import render
from GestCommApp.models import Article, Client, Devis, Facture, LigneFacture
from GestCommApp.serializers import (
    ArticleSerializer, ClientSerializer, DevisSerializer, FactureSerializer)
from GestCommApp.assistant import answer as assistant_answer
from rest_framework import generics, status
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


class DevisConvertir(APIView):
    """POST /api/devis/<id>/convertir — turn a validated devis into a
    brouillon facture, copying client and lines."""

    @transaction.atomic
    def post(self, request, pk):
        devis = Devis.objects.filter(pk=pk).first()
        if devis is None:
            raise Http404
        if devis.statutDevis != Devis.STATUT_VALIDE:
            return Response(
                {"detail": "Only a 'valide' devis can be converted "
                           f"(current: '{devis.statutDevis}')."},
                status=status.HTTP_400_BAD_REQUEST)

        facture = Facture.objects.create(
            codeFacture=request.data.get(
                "codeFacture", "F%04d" % devis.idDevis),
            dateFacture=request.data.get(
                "dateFacture", devis.dateDevis),
            client=devis.client,
            devis=devis,
            statutFacture=Facture.STATUT_BROUILLON,
            observationFacture=request.data.get(
                "observationFacture", devis.observationDevis))
        for line in devis.lignes.all():
            LigneFacture.objects.create(
                facture=facture,
                article=line.article,
                designation=line.designation,
                quantite=line.quantite,
                prixUnitaire=line.prixUnitaire,
                remise=line.remise,
                tva=line.tva)

        devis.statutDevis = Devis.STATUT_CONVERTI
        devis.save(update_fields=['statutDevis'])

        return Response(
            FactureSerializer(facture).data,
            status=status.HTTP_201_CREATED)


class AssistantAsk(APIView):
    """POST /api/assistant/ask {question} — deterministic copilot intents.

    Read-only by design: it answers questions about clients using the same
    ORM the REST API exposes. Write intents (create/update) are deliberately
    absent until a confirmation flow exists.
    """

    def post(self, request):
        question = request.data.get("question", "")
        return Response(assistant_answer(question))
