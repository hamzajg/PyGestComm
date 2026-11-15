from django.shortcuts import render
from GestCommApp.models import Client
from GestCommApp.serializers import ClientSerializer
from GestCommApp.assistant import answer as assistant_answer
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

# Create your views here.

class ClientList(generics.ListCreateAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


class AssistantAsk(APIView):
    """POST /api/assistant/ask {question} — deterministic copilot intents.

    Read-only by design: it answers questions about clients using the same
    ORM the REST API exposes. Write intents (create/update) are deliberately
    absent until a confirmation flow exists.
    """

    def post(self, request):
        question = request.data.get("question", "")
        return Response(assistant_answer(question))