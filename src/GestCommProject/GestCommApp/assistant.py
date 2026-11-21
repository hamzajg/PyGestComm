"""Deterministic assistant intents over the domain resources.

This is the copilot's *tool surface*, not an LLM: `answer()` maps a small
set of intents onto ORM queries and returns structured results. A future
LLM front-end (the orca/al-minhej pattern) would translate free text into
these same intents — the contract stays stable either way.

Resources: clients, articles, devis (quotes), factures (invoices),
bonlivs (delivery notes).

Intents today (KISS — extend only when a real caller needs it):
  - count        "how many clients/articles/devis/factures"
  - search       "find <resource> <term>", "<resource> <term>", or a
                 bare term (searched against clients, then articles)
  - help         anything else → describes what it can do
"""

import re

from django.db.models import Q

from GestCommApp.models import Article, BonLiv, Client, Devis, Facture
from GestCommApp.phones import searchable_phone

_COUNT_RE = re.compile(
    r"(how many|combien|nombre de|count|total)\s*(.*)", re.IGNORECASE)
_SEARCH_RE = re.compile(
    r"(find|search|lookup|show|get|list|trouver|chercher|afficher)\s*(.*)",
    re.IGNORECASE)

_RESOURCES = {
    'client': Client,
    'article': Article,
    'devis': Devis,
    'facture': Facture,
    'bonliv': BonLiv,
}

_PLURALS = {
    'client': 'clients', 'article': 'articles',
    'devis': 'devis', 'facture': 'factures',
    'bonliv': 'bons de livraison',
}

# Plural/French aliases → canonical resource key.
_ALIASES = {
    'client': 'client', 'clients': 'client',
    'clientèle': 'client', 'clientele': 'client',
    'article': 'article', 'articles': 'article',
    'produit': 'article', 'produits': 'article',
    'devis': 'devis', 'quote': 'devis', 'quotes': 'devis',
    'proforma': 'devis',
    'facture': 'facture', 'factures': 'facture',
    'invoice': 'facture', 'invoices': 'facture',
    'bonliv': 'bonliv', 'bons de livraison': 'bonliv',
    'livraison': 'bonliv', 'delivery': 'bonliv',
    'delivery note': 'bonliv',
}

_RESOURCE_WORDS = {
    'client': ('client', 'clients', 'clientèle', 'clientele'),
    'article': ('article', 'articles', 'produit', 'produits'),
    'devis': ('devis', 'quote', 'quotes', 'proforma'),
    'facture': ('facture', 'factures', 'invoice', 'invoices'),
    'bonliv': ('bonliv', 'bons de livraison', 'livraison',
               'delivery', 'delivery note'),
}

# Model-name suffix used in field names (statutBonLiv, not statutBonliv).
_DOC_SUFFIX = {
    'devis': 'Devis',
    'facture': 'Facture',
    'bonliv': 'BonLiv',
}


def _client_brief(client):
    return {
        "idClient": client.idClient,
        "codeClient": client.codeClient,
        "nomPrenomClient": client.nomPrenomClient,
        "matFiscalClient": client.matFiscalClient,
        "numTelClient1": client.numTelClient1,
        "numTelClient2": client.numTelClient2,
    }


def _article_brief(article):
    return {
        "idArticle": article.idArticle,
        "refArticle": article.refArticle,
        "descArticle": article.descArticle,
        "prixVenteUnitaire": str(article.prixVenteUnitaire),
    }


def _document_brief(doc, kind):
    suffix = _DOC_SUFFIX[kind]
    client = doc.client
    brief = {
        "id" + suffix: getattr(doc, "id" + suffix),
        "code" + suffix: getattr(doc, "code" + suffix),
        "date" + suffix: str(getattr(doc, "date" + suffix)),
        "codeClient": client.codeClient,
        "nomPrenomClient": client.nomPrenomClient,
        "statut" + suffix: getattr(doc, "statut" + suffix),
        "nbLignes": doc.lignes.count(),
    }
    return brief


def _search_clients(term):
    term = term.strip()
    if not term:
        return Client.objects.none()
    qs = Client.objects.filter(
        Q(codeClient__icontains=term)
        | Q(nomPrenomClient__icontains=term)
        | Q(matFiscalClient__icontains=term)
        | Q(addresseClient1__icontains=term)
        | Q(addresseClient2__icontains=term)
    )
    # Phones are stored canonically, so a formatted term such as
    # "06 12 34 56 78" is reduced to its digits before matching.
    phone = searchable_phone(term)
    if phone:
        qs = qs | Client.objects.filter(
            Q(numTelClient1__contains=phone)
            | Q(numTelClient2__contains=phone))
    return qs.distinct()


def _search_articles(term):
    term = term.strip()
    if not term:
        return Article.objects.none()
    return Article.objects.filter(
        Q(refArticle__icontains=term) | Q(descArticle__icontains=term)
    ).distinct()


def _search_documents(model, term, kind):
    term = term.strip()
    if not term:
        return model.objects.none()
    code_field = 'code' + _DOC_SUFFIX[kind]
    qs = model.objects.filter(
        Q(**{code_field + '__icontains': term})
        | Q(client__codeClient__icontains=term)
        | Q(client__nomPrenomClient__icontains=term)
    )
    if kind == 'facture':
        qs = qs | model.objects.filter(devis__codeDevis__icontains=term)
    return qs.distinct()


def _brief(resource, obj):
    if resource == 'client':
        return _client_brief(obj)
    if resource == 'article':
        return _article_brief(obj)
    return _document_brief(obj, resource)


def _search(resource, term):
    if resource == 'client':
        return _search_clients(term)
    if resource == 'article':
        return _search_articles(term)
    return _search_documents(_RESOURCES[resource], term, resource)


def _resource_from_words(words):
    """First word that names a resource, else None."""
    for word in words:
        key = word.lower().strip('.,:;!?')
        if key in _ALIASES:
            return _ALIASES[key]
    return None


def _strip_resource_words(text):
    """Remove resource keywords, returning the leftover search term."""
    words = [w for w in text.split()
             if w.lower().strip('.,:;!?') not in _ALIASES]
    return ' '.join(words).strip(' :,-')


def _help():
    return {
        "intent": "help",
        "answer": (
            "I can answer questions about clients, articles, devis, "
            "factures and bons de livraison: 'how many clients', "
            "'find article <ref>', 'find devis <code/client>'. Records "
            "can also be listed and created via /api/client, "
            "/api/article, /api/devis, /api/facture, /api/bonliv."
        ),
        "data": None,
    }


def _result(resource, term, items):
    key = _PLURALS[resource]
    noun = key if len(items) != 1 else resource
    return {
        "intent": "search",
        "answer": f"{len(items)} {noun} matching '{term}'.",
        "data": {"query": term, "resource": resource, key:
                 [_brief(resource, o) for o in items]},
    }


def _count_answer(resource):
    total = _RESOURCES[resource].objects.count()
    noun = _PLURALS[resource] if total != 1 else resource
    return {
        "intent": "count",
        "answer": f"{total} {noun} in the registry.",
        "data": {"count": total, "resource": resource},
    }


def answer(question):
    """Map a question string to {intent, answer, data}. Never raises on
    unrecognized input — falls back to help."""
    if not isinstance(question, str) or not question.strip():
        return {
            "intent": "help",
            "answer": ("Ask me about clients, articles, devis, factures "
                       "or bons de livraison — e.g. 'how many articles' "
                       "or 'find devis D001'."),
            "data": None,
        }

    text = question.strip()

    count_match = _COUNT_RE.search(text)
    if count_match:
        resource = _resource_from_words(count_match.group(2).split())
        # "how many" with no resource word historically meant clients.
        return _count_answer(resource or 'client')

    search_match = _SEARCH_RE.search(text)
    if search_match:
        rest = (search_match.group(2) or "").strip(" :,-")
        resource = _resource_from_words(rest.split())
        term = _strip_resource_words(rest)
        if not term:
            # Verb-only input ("find client") → fall back to bare-term scan.
            term = _strip_resource_words(
                re.sub(r"\b(find|search|lookup|show|get|list|trouver|"
                       r"chercher|afficher)\b", "", text,
                       flags=re.IGNORECASE))
        resource = resource or 'client'
        items = list(_search(resource, term)[:20])
        return _result(resource, term, items)

    # No recognized intent: a bare "<resource> <term>" or plain term still
    # searches — resource word routes it, otherwise clients then articles.
    words = text.split()
    resource = _resource_from_words(words)
    term = _strip_resource_words(text)
    if resource and term:
        items = list(_search(resource, term)[:20])
        return _result(resource, term, items)

    if len(text) >= 3:
        clients = list(_search_clients(text)[:20])
        if clients:
            return _result('client', text, clients)
        articles = list(_search_articles(text)[:20])
        if articles:
            return _result('article', text, articles)
        return {
            "intent": "search",
            "answer": f"0 results matching '{text}'.",
            "data": {"query": text, "resource": None, "results": []},
        }

    return _help()
