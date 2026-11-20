import re
from decimal import Decimal

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
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


# Document auto-numbering (specs/document-numbering): when a create
# payload omits the code, assign PREFIX + next sequence number. The
# sequence is the max trailing digit run among codes carrying the
# prefix, so deletions never cause reuse.
_CODE_PREFIXES = {'codeDevis': 'DEV-', 'codeFacture': 'FAC-',
                  'codeBonLiv': 'BL-'}
_CODE_MODELS = {'codeDevis': Devis, 'codeFacture': Facture,
                'codeBonLiv': BonLiv}


def _next_document_code(field_name):
    model = _CODE_MODELS[field_name]
    prefix = _CODE_PREFIXES[field_name]
    highest = 0
    for code in model.objects.filter(
            **{field_name + '__startswith': prefix}
    ).values_list(field_name, flat=True):
        match = re.search(r'(\d+)$', code)
        if match:
            highest = max(highest, int(match.group(1)))
    return '%s%04d' % (prefix, highest + 1)


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
        if not validated_data.get('codeDevis'):
            validated_data['codeDevis'] = _next_document_code('codeDevis')
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
        if not validated_data.get('codeFacture'):
            validated_data['codeFacture'] = _next_document_code(
                'codeFacture')
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
        if not validated_data.get('codeBonLiv'):
            validated_data['codeBonLiv'] = _next_document_code('codeBonLiv')
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


class UserProfileSerializer(serializers.ModelSerializer):
    """Identity of the signed-in account, as the desktop client sees it.

    The role is derived here, never supplied by the caller: `is_staff` is the
    flag Django admin already gates on, so accounts created before this
    endpoint keep working without a migration (SPEC D1).
    """

    firstName = serializers.CharField(
        source='first_name', required=False, allow_blank=True)
    lastName = serializers.CharField(
        source='last_name', required=False, allow_blank=True)
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'firstName', 'lastName', 'email', 'role')
        read_only_fields = ('id', 'username', 'role')

    def get_role(self, obj):
        return 'admin' if obj.is_staff else 'operator'


class PasswordChangeSerializer(serializers.Serializer):
    """Self-service password change: the current password is the proof."""

    currentPassword = serializers.CharField(write_only=True)
    newPassword = serializers.CharField(write_only=True)

    def validate_currentPassword(self, value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError(
                'Mot de passe actuel incorrect.')
        return value

    def validate_newPassword(self, value):
        try:
            validate_password(value, self.context['request'].user)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages))
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['newPassword'])
        user.save(update_fields=['password'])
        return user
