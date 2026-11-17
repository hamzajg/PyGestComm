from django.db import transaction
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render
from GestCommApp.models import (
    Article, BonLiv, Client, Devis, Facture, LigneFacture)
from GestCommApp.serializers import (
    ArticleSerializer, BonLivSerializer, ClientSerializer, DevisSerializer,
    FactureSerializer)
from GestCommApp.assistant import answer as assistant_answer
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

# Create your views here.


def _search_param(request, *fields):
    term = request.query_params.get('search', '').strip()
    if not term:
        return None
    query = Q()
    for field in fields:
        query |= Q(**{field + '__icontains': term})
    return query


class ClientList(generics.ListCreateAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        query = _search_param(
            self.request, 'codeClient', 'nomPrenomClient',
            'matFiscalClient')
        return qs.filter(query) if query else qs


class ClientDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


class ArticleList(generics.ListCreateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        query = _search_param(self.request, 'refArticle', 'descArticle')
        return qs.filter(query) if query else qs


class ArticleDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer


def _document_queryset(request, model):
    qs = model.objects.prefetch_related('lignes__article')
    suffix = model.__name__  # Devis → statutDevis/codeDevis (BonLiv → BonLiv)
    statut = request.query_params.get('statut')
    if statut:
        qs = qs.filter(**{'statut' + suffix: statut})
    client_id = request.query_params.get('client')
    if client_id:
        qs = qs.filter(client_id=client_id)
    term = request.query_params.get('search', '').strip()
    if term:
        query = (
            Q(**{'code' + suffix + '__icontains': term})
            | Q(client__codeClient__icontains=term)
            | Q(client__nomPrenomClient__icontains=term))
        if model is Facture:
            query |= Q(devis__codeDevis__icontains=term)
        qs = qs.filter(query)
    return qs


class DevisList(generics.ListCreateAPIView):
    serializer_class = DevisSerializer

    def get_queryset(self):
        return _document_queryset(self.request, Devis)


class FactureList(generics.ListCreateAPIView):
    serializer_class = FactureSerializer

    def get_queryset(self):
        return _document_queryset(self.request, Facture)


class BonLivList(generics.ListCreateAPIView):
    serializer_class = BonLivSerializer

    def get_queryset(self):
        return _document_queryset(self.request, BonLiv)


def _locked_detail(view, request, *args, **kwargs):
    """Reject writes on terminal-state documents."""
    instance = view.get_object()
    locked_statuts = {
        'Facture': (Facture.STATUT_PAYEE, Facture.STATUT_ANNULEE),
        'Devis': (Devis.STATUT_CONVERTI,),
        'BonLiv': (BonLiv.STATUT_LIVRE, BonLiv.STATUT_ANNULE),
    }[type(instance).__name__]
    statut_field = 'statut' + type(instance).__name__
    if getattr(instance, statut_field) in locked_statuts:
        return Response(
            {"detail": f"A '{getattr(instance, statut_field)}' "
                       f"{type(instance).__name__.lower()} cannot be "
                       "modified or deleted."},
            status=status.HTTP_400_BAD_REQUEST)
    return None


class DevisDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Devis.objects.prefetch_related('lignes__article')
    serializer_class = DevisSerializer

    def update(self, request, *args, **kwargs):
        blocked = _locked_detail(self, request, *args, **kwargs)
        return blocked or super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        blocked = _locked_detail(self, request, *args, **kwargs)
        return blocked or super().destroy(request, *args, **kwargs)


class FactureDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Facture.objects.prefetch_related('lignes__article')
    serializer_class = FactureSerializer

    def update(self, request, *args, **kwargs):
        blocked = _locked_detail(self, request, *args, **kwargs)
        return blocked or super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        blocked = _locked_detail(self, request, *args, **kwargs)
        return blocked or super().destroy(request, *args, **kwargs)


class BonLivDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = BonLiv.objects.prefetch_related('lignes__article')
    serializer_class = BonLivSerializer

    def update(self, request, *args, **kwargs):
        blocked = _locked_detail(self, request, *args, **kwargs)
        return blocked or super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        blocked = _locked_detail(self, request, *args, **kwargs)
        return blocked or super().destroy(request, *args, **kwargs)


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
