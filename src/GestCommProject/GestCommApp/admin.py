from django.contrib import admin

from GestCommApp.models import (
    Article, Client, Devis, Facture, LigneDevis, LigneFacture)


class LigneDevisInline(admin.TabularInline):
    model = LigneDevis
    extra = 0


class LigneFactureInline(admin.TabularInline):
    model = LigneFacture
    extra = 0


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    pass


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    pass


@admin.register(Devis)
class DevisAdmin(admin.ModelAdmin):
    inlines = [LigneDevisInline]


@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):
    inlines = [LigneFactureInline]
