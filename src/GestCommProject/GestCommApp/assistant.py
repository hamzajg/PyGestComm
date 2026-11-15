"""Deterministic assistant intents over the Client resource.

This is the copilot's *tool surface*, not an LLM: `answer()` maps a small
set of intents onto ORM queries and returns structured results. A future
LLM front-end (the orca/al-minhej pattern) would translate free text into
these same intents — the contract stays stable either way.

Intents today (KISS — extend only when a real caller needs it):
  - count        "how many clients", "combien de clients"
  - search       "find client <term>", "client <term>", "<term>" alone
  - help         anything else → describes what it can do
"""

import re

from django.db.models import Q

from GestCommApp.models import Client

_INTENT_PATTERNS = [
    ("count", re.compile(
        r"(how many|combien|nombre de|count|total).*(client|clientèle)?",
        re.IGNORECASE)),
    ("search", re.compile(
        r"(find|search|lookup|show|get|list|trouver|chercher|afficher|client)\s*(.*)",
        re.IGNORECASE)),
]


def _client_brief(client):
    return {
        "idClient": client.idClient,
        "codeClient": client.codeClient,
        "nomPrenomClient": client.nomPrenomClient,
        "matFiscalClient": client.matFiscalClient,
        "numTelClient1": client.numTelClient1,
        "numTelClient2": client.numTelClient2,
    }


def _search_clients(term):
    term = term.strip()
    if not term:
        return Client.objects.none()
    # Phones are IntegerFields — try a numeric match when the term is digits.
    qs = Client.objects.filter(
        Q(codeClient__icontains=term)
        | Q(nomPrenomClient__icontains=term)
        | Q(matFiscalClient__icontains=term)
        | Q(addresseClient1__icontains=term)
        | Q(addresseClient2__icontains=term)
    )
    if term.isdigit():
        qs = qs | Client.objects.filter(
            Q(numTelClient1=int(term)) | Q(numTelClient2=int(term)))
    return qs.distinct()


def _help():
    return {
        "intent": "help",
        "answer": (
            "I can answer questions about clients: 'how many clients', "
            "'find client <name/code/tax-id/phone>'. Client records can "
            "also be listed and created via /api/client."
        ),
        "data": None,
    }


def answer(question):
    """Map a question string to {intent, answer, data}. Never raises on
    unrecognized input — falls back to help."""
    if not isinstance(question, str) or not question.strip():
        return {
            "intent": "help",
            "answer": "Ask me about clients — e.g. 'how many clients' or 'find client C001'.",
            "data": None,
        }

    text = question.strip()

    if _INTENT_PATTERNS[0][1].search(text):  # count
        total = Client.objects.count()
        return {
            "intent": "count",
            "answer": f"{total} client{'s' if total != 1 else ''} in the registry.",
            "data": {"count": total},
        }

    search_match = _INTENT_PATTERNS[1][1].search(text)
    if search_match:
        term = (search_match.group(2) or "").strip(" :,-")
        # Drop a leading "client(s)" the pattern left in the term.
        term = re.sub(r"^clients?\s+", "", term, flags=re.IGNORECASE).strip(" :,-")
        # Bare "client" or verb-only input → search the remaining words.
        if not term:
            term = re.sub(r"\b(find|search|lookup|show|get|list|trouver|chercher|afficher|client)\b",
                          "", text, flags=re.IGNORECASE).strip(" :,-")
        clients = list(_search_clients(term)[:20])
        return {
            "intent": "search",
            "answer": (
                f"{len(clients)} client{'s' if len(clients) != 1 else ''} "
                f"matching '{term}'."
            ),
            "data": {"query": term, "clients": [_client_brief(c) for c in clients]},
        }

    # No recognized intent: treat the whole text as a search term — a bare
    # name or code should still find the client. Only trivially short input
    # falls through to help.
    if len(text) >= 3:
        clients = list(_search_clients(text)[:20])
        return {
            "intent": "search",
            "answer": (
                f"{len(clients)} client{'s' if len(clients) != 1 else ''} "
                f"matching '{text}'."
            ),
            "data": {"query": text, "clients": [_client_brief(c) for c in clients]},
        }

    return _help()
