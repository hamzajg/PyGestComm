from decimal import Decimal

from django.db import transaction
from rest_framework import serializers

from GestCommApp.models import (
    Article, BonLiv, Client, Devis, Facture, LigneBonLiv, LigneDevis,
    LigneFacture)

CENT = Decimal('0.01')


class ClientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Client
        fields = '__all__'


class ArticleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Article
        fields = '__all__'


def _money(value):
    return Decimal(value).quantize(CENT)


def _line_totals(lines):
    """Sum HT/TVA over unsaved or saved line instances."""
    ht = sum((line.total_ht for line in lines), Decimal('0'))
    tva = sum((line.total_tva for line in lines), Decimal('0'))
    return {
        'totalHT': _money(ht),
        'totalTVA': _money(tva),
        'totalTTC': _money(ht + tva),
    }


def _document_totals(document):
    return _line_totals(document.lignes.all())


def _resolve_line_data(line_data, price_field):
    """Fill designation/prix/remise/tva defaults from the linked article.

    `prix_field` is the article attribute used as fallback unit price
    ('prixVenteUnitaire' — both devis and facture sell at sale price).
    """
    data = dict(line_data)
    article = data.get('article')
    if article is not None:
        if not data.get('designation'):
            data['designation'] = article.descArticle
        if data.get('prixUnitaire') is None:
            data['prixUnitaire'] = getattr(article, price_field)
        if data.get('remise') is None:
            data['remise'] = article.remiseVente
        if data.get('tva') is None:
            data['tva'] = article.tvaVente
    if not data.get('designation'):
        raise serializers.ValidationError(
            {'designation': 'Required when no article is linked.'})
    if data.get('prixUnitaire') is None:
        raise serializers.ValidationError(
            {'prixUnitaire': 'Required when no article is linked.'})
    return data


def _save_lines(line_model, document, lines_data, fk_name, price_field):
    for raw in lines_data:
        data = _resolve_line_data(raw, price_field)
        data.pop(fk_name, None)  # document FK is set explicitly
        line_model.objects.create(**{fk_name: document}, **data)


class LigneDevisSerializer(serializers.ModelSerializer):
    devis = serializers.PrimaryKeyRelatedField(read_only=True)
    article = serializers.PrimaryKeyRelatedField(
        queryset=Article.objects.all(), required=False, allow_null=True)
    designation = serializers.CharField(
        max_length=200, required=False, allow_blank=True)
    totalHT = serializers.SerializerMethodField()
    totalTVA = serializers.SerializerMethodField()

    class Meta:
        model = LigneDevis
        fields = '__all__'
        read_only_fields = ('idLigneDevis',)

    def get_totalHT(self, obj):
        return _money(obj.total_ht)

    def get_totalTVA(self, obj):
        return _money(obj.total_tva)


class DevisSerializer(serializers.ModelSerializer):
    lignes = LigneDevisSerializer(many=True, required=False)
    codeClient = serializers.CharField(
        source='client.codeClient', read_only=True)
    nomPrenomClient = serializers.CharField(
        source='client.nomPrenomClient', read_only=True)
    totalHT = serializers.SerializerMethodField()
    totalTVA = serializers.SerializerMethodField()
    totalTTC = serializers.SerializerMethodField()

    class Meta:
        model = Devis
        fields = '__all__'
        read_only_fields = ('idDevis',)

    def get_totalHT(self, obj):
        return _money(_document_totals(obj)['totalHT'])

    def get_totalTVA(self, obj):
        return _money(_document_totals(obj)['totalTVA'])

    def get_totalTTC(self, obj):
        return _money(_document_totals(obj)['totalTTC'])

    @transaction.atomic
    def create(self, validated_data):
        lines = validated_data.pop('lignes', [])
        devis = Devis.objects.create(**validated_data)
        _save_lines(LigneDevis, devis, lines, 'devis', 'prixVenteUnitaire')
        return devis

    @transaction.atomic
    def update(self, instance, validated_data):
        lines = validated_data.pop('lignes', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if lines is not None:
            instance.lignes.all().delete()
            _save_lines(
                LigneDevis, instance, lines, 'devis', 'prixVenteUnitaire')
        return instance


class LigneFactureSerializer(serializers.ModelSerializer):
    facture = serializers.PrimaryKeyRelatedField(read_only=True)
    article = serializers.PrimaryKeyRelatedField(
        queryset=Article.objects.all(), required=False, allow_null=True)
    designation = serializers.CharField(
        max_length=200, required=False, allow_blank=True)
    totalHT = serializers.SerializerMethodField()
    totalTVA = serializers.SerializerMethodField()

    class Meta:
        model = LigneFacture
        fields = '__all__'
        read_only_fields = ('idLigneFacture',)

    def get_totalHT(self, obj):
        return _money(obj.total_ht)

    def get_totalTVA(self, obj):
        return _money(obj.total_tva)


class FactureSerializer(serializers.ModelSerializer):
    lignes = LigneFactureSerializer(many=True, required=False)
    codeClient = serializers.CharField(
        source='client.codeClient', read_only=True)
    nomPrenomClient = serializers.CharField(
        source='client.nomPrenomClient', read_only=True)
    codeDevis = serializers.CharField(
        source='devis.codeDevis', read_only=True)
    totalHT = serializers.SerializerMethodField()
    totalTVA = serializers.SerializerMethodField()
    totalTTC = serializers.SerializerMethodField()

    class Meta:
        model = Facture
        fields = '__all__'
        read_only_fields = ('idFacture',)

    def get_totalHT(self, obj):
        return _money(_document_totals(obj)['totalHT'])

    def get_totalTVA(self, obj):
        return _money(_document_totals(obj)['totalTVA'])

    def get_totalTTC(self, obj):
        return _money(_document_totals(obj)['totalTTC'])

    @transaction.atomic
    def create(self, validated_data):
        lines = validated_data.pop('lignes', [])
        facture = Facture.objects.create(**validated_data)
        _save_lines(LigneFacture, facture, lines, 'facture',
                    'prixVenteUnitaire')
        return facture

    @transaction.atomic
    def update(self, instance, validated_data):
        lines = validated_data.pop('lignes', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if lines is not None:
            instance.lignes.all().delete()
            _save_lines(
                LigneFacture, instance, lines, 'facture',
                'prixVenteUnitaire')
        return instance


class LigneBonLivSerializer(serializers.ModelSerializer):
    bonliv = serializers.PrimaryKeyRelatedField(read_only=True)
    article = serializers.PrimaryKeyRelatedField(
        queryset=Article.objects.all(), required=False, allow_null=True)
    designation = serializers.CharField(
        max_length=200, required=False, allow_blank=True)
    totalHT = serializers.SerializerMethodField()
    totalTVA = serializers.SerializerMethodField()

    class Meta:
        model = LigneBonLiv
        fields = '__all__'
        read_only_fields = ('idLigneBonLiv',)

    def get_totalHT(self, obj):
        return _money(obj.total_ht)

    def get_totalTVA(self, obj):
        return _money(obj.total_tva)


class BonLivSerializer(serializers.ModelSerializer):
    lignes = LigneBonLivSerializer(many=True, required=False)
    codeClient = serializers.CharField(
        source='client.codeClient', read_only=True)
    nomPrenomClient = serializers.CharField(
        source='client.nomPrenomClient', read_only=True)
    totalHT = serializers.SerializerMethodField()
    totalTVA = serializers.SerializerMethodField()
    totalTTC = serializers.SerializerMethodField()

    class Meta:
        model = BonLiv
        fields = '__all__'
        read_only_fields = ('idBonLiv',)

    def get_totalHT(self, obj):
        return _money(_document_totals(obj)['totalHT'])

    def get_totalTVA(self, obj):
        return _money(_document_totals(obj)['totalTVA'])

    def get_totalTTC(self, obj):
        return _money(_document_totals(obj)['totalTTC'])

    @transaction.atomic
    def create(self, validated_data):
        lines = validated_data.pop('lignes', [])
        bonliv = BonLiv.objects.create(**validated_data)
        _save_lines(LigneBonLiv, bonliv, lines, 'bonliv',
                    'prixVenteUnitaire')
        return bonliv

    @transaction.atomic
    def update(self, instance, validated_data):
        lines = validated_data.pop('lignes', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if lines is not None:
            instance.lignes.all().delete()
            _save_lines(LigneBonLiv, instance, lines, 'bonliv',
                        'prixVenteUnitaire')
        return instance
