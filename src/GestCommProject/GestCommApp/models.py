from decimal import Decimal

from django.db import models
from django.utils import timezone

# Create your models here.


class Client(models.Model):
    idClient = models.AutoField(primary_key=True)
    codeClient = models.CharField(max_length=20)
    nomPrenomClient = models.CharField(max_length=100)
    matFiscalClient = models.CharField(max_length=100)
    addresseClient1 = models.CharField(max_length=100)
    addresseClient2 = models.CharField(max_length=100)
    numTelClient1 = models.IntegerField()
    numTelClient2 = models.IntegerField()

    def __str__(self):
        return '%d: %s' % (self.idClient, self.codeClient)

    class Meta:
        db_table = "client"
        unique_together = ('idClient', 'codeClient')
        ordering = ['codeClient']


class Article(models.Model):
    """Sellable item — field set mirrors the Gest_Comm_ClientFX Article
    POJO (snake_case there, camelCase here like Client)."""

    idArticle = models.AutoField(primary_key=True)
    refArticle = models.CharField(max_length=50)
    descArticle = models.CharField(max_length=200)
    prixAchatUnitaire = models.DecimalField(
        max_digits=12, decimal_places=2, default=0)
    remiseAchat = models.FloatField(default=0)
    tvaAchat = models.FloatField(default=0)
    prixVenteUnitaire = models.DecimalField(
        max_digits=12, decimal_places=2, default=0)
    remiseVente = models.FloatField(default=0)
    tvaVente = models.FloatField(default=0)
    dernierPrixVenteUnitaire = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return '%d: %s' % (self.idArticle, self.refArticle)

    class Meta:
        db_table = "article"
        ordering = ['refArticle']


class Devis(models.Model):
    STATUT_BROUILLON = 'brouillon'
    STATUT_VALIDE = 'valide'
    STATUT_REFUSE = 'refuse'
    STATUT_CONVERTI = 'converti'
    STATUT_CHOICES = [
        (STATUT_BROUILLON, 'Brouillon'),
        (STATUT_VALIDE, 'Validé'),
        (STATUT_REFUSE, 'Refusé'),
        (STATUT_CONVERTI, 'Converti'),
    ]

    idDevis = models.AutoField(primary_key=True)
    codeDevis = models.CharField(max_length=20)
    dateDevis = models.DateField(default=timezone.localdate)
    client = models.ForeignKey(
        Client, on_delete=models.PROTECT, related_name='devis')
    statutDevis = models.CharField(
        max_length=20, choices=STATUT_CHOICES, default=STATUT_BROUILLON)
    observationDevis = models.CharField(max_length=500, blank=True, default='')

    def __str__(self):
        return '%d: %s' % (self.idDevis, self.codeDevis)

    class Meta:
        db_table = "devis"
        ordering = ['-dateDevis', 'codeDevis']


class LigneDevis(models.Model):
    idLigneDevis = models.AutoField(primary_key=True)
    devis = models.ForeignKey(
        Devis, on_delete=models.CASCADE, related_name='lignes')
    article = models.ForeignKey(
        Article, on_delete=models.PROTECT, null=True, blank=True,
        related_name='+')
    designation = models.CharField(max_length=200)
    quantite = models.DecimalField(
        max_digits=10, decimal_places=2, default=1)
    prixUnitaire = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True)
    remise = models.FloatField(default=0)
    tva = models.FloatField(default=0)

    class Meta:
        db_table = "ligne_devis"
        ordering = ['idLigneDevis']

    @property
    def prix_effectif(self):
        if self.prixUnitaire is not None:
            return self.prixUnitaire
        if self.article is not None:
            return self.article.prixVenteUnitaire
        return Decimal('0')

    @property
    def total_ht(self):
        return (self.quantite * self.prix_effectif
                * (Decimal('1') - Decimal(str(self.remise)) / 100))

    @property
    def total_tva(self):
        return self.total_ht * Decimal(str(self.tva)) / 100


class Facture(models.Model):
    STATUT_BROUILLON = 'brouillon'
    STATUT_VALIDEE = 'validee'
    STATUT_PAYEE = 'payee'
    STATUT_ANNULEE = 'annulee'
    STATUT_CHOICES = [
        (STATUT_BROUILLON, 'Brouillon'),
        (STATUT_VALIDEE, 'Validée'),
        (STATUT_PAYEE, 'Payée'),
        (STATUT_ANNULEE, 'Annulée'),
    ]

    idFacture = models.AutoField(primary_key=True)
    codeFacture = models.CharField(max_length=20)
    dateFacture = models.DateField(default=timezone.localdate)
    client = models.ForeignKey(
        Client, on_delete=models.PROTECT, related_name='factures')
    devis = models.ForeignKey(
        'Devis', on_delete=models.PROTECT, null=True, blank=True,
        related_name='factures')
    statutFacture = models.CharField(
        max_length=20, choices=STATUT_CHOICES, default=STATUT_BROUILLON)
    observationFacture = models.CharField(
        max_length=500, blank=True, default='')

    def __str__(self):
        return '%d: %s' % (self.idFacture, self.codeFacture)

    class Meta:
        db_table = "facture"
        ordering = ['-dateFacture', 'codeFacture']


class LigneFacture(models.Model):
    idLigneFacture = models.AutoField(primary_key=True)
    facture = models.ForeignKey(
        Facture, on_delete=models.CASCADE, related_name='lignes')
    article = models.ForeignKey(
        Article, on_delete=models.PROTECT, null=True, blank=True,
        related_name='+')
    designation = models.CharField(max_length=200)
    quantite = models.DecimalField(
        max_digits=10, decimal_places=2, default=1)
    prixUnitaire = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True)
    remise = models.FloatField(default=0)
    tva = models.FloatField(default=0)

    class Meta:
        db_table = "ligne_facture"
        ordering = ['idLigneFacture']

    @property
    def prix_effectif(self):
        if self.prixUnitaire is not None:
            return self.prixUnitaire
        if self.article is not None:
            return self.article.prixVenteUnitaire
        return Decimal('0')

    @property
    def total_ht(self):
        return (self.quantite * self.prix_effectif
                * (Decimal('1') - Decimal(str(self.remise)) / 100))

    @property
    def total_tva(self):
        return self.total_ht * Decimal(str(self.tva)) / 100


class BonLiv(models.Model):
    """Bon de livraison (delivery note) — same document shape as Devis:
    header + nested lines, client FK, statut workflow."""

    STATUT_BROUILLON = 'brouillon'
    STATUT_VALIDE = 'valide'
    STATUT_LIVRE = 'livre'
    STATUT_ANNULE = 'annule'
    STATUT_CHOICES = [
        (STATUT_BROUILLON, 'Brouillon'),
        (STATUT_VALIDE, 'Validé'),
        (STATUT_LIVRE, 'Livré'),
        (STATUT_ANNULE, 'Annulé'),
    ]

    idBonLiv = models.AutoField(primary_key=True)
    codeBonLiv = models.CharField(max_length=20)
    dateBonLiv = models.DateField(default=timezone.localdate)
    client = models.ForeignKey(
        Client, on_delete=models.PROTECT, related_name='bonlivs')
    statutBonLiv = models.CharField(
        max_length=20, choices=STATUT_CHOICES, default=STATUT_BROUILLON)
    observationBonLiv = models.CharField(
        max_length=500, blank=True, default='')

    def __str__(self):
        return '%d: %s' % (self.idBonLiv, self.codeBonLiv)

    class Meta:
        db_table = "bonliv"
        ordering = ['-dateBonLiv', 'codeBonLiv']


class LigneBonLiv(models.Model):
    idLigneBonLiv = models.AutoField(primary_key=True)
    bonliv = models.ForeignKey(
        BonLiv, on_delete=models.CASCADE, related_name='lignes')
    article = models.ForeignKey(
        Article, on_delete=models.PROTECT, null=True, blank=True,
        related_name='+')
    designation = models.CharField(max_length=200)
    quantite = models.DecimalField(
        max_digits=10, decimal_places=2, default=1)
    prixUnitaire = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True)
    remise = models.FloatField(default=0)
    tva = models.FloatField(default=0)

    class Meta:
        db_table = "ligne_bonliv"
        ordering = ['idLigneBonLiv']

    @property
    def prix_effectif(self):
        if self.prixUnitaire is not None:
            return self.prixUnitaire
        if self.article is not None:
            return self.article.prixVenteUnitaire
        return Decimal('0')

    @property
    def total_ht(self):
        return (self.quantite * self.prix_effectif
                * (Decimal('1') - Decimal(str(self.remise)) / 100))

    @property
    def total_tva(self):
        return self.total_ht * Decimal(str(self.tva)) / 100


# ManyToManyField = models.ManyToManyField(Group)
# ManyToManyField = models.ManyToManyField(User)
