from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from GestCommApp.models import Client

CLIENT = {
    "codeClient": "C001",
    "nomPrenomClient": "Ada Lovelace",
    "matFiscalClient": "1234567",
    "addresseClient1": "1 Analytical Engine Way",
    "addresseClient2": "Suite 2",
    "numTelClient1": 11111111,
    "numTelClient2": 22222222,
}


class ClientModelTests(TestCase):
    def test_create_client(self):
        client = Client.objects.create(**CLIENT)

        self.assertEqual(str(client), "%d: C001" % client.idClient)


class ClientApiTest(APITestCase):
    url = "/api/client"

    def test_lists_every_field_of_each_client(self):
        Client.objects.create(**CLIENT)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0], {"idClient": 1, **CLIENT})

    def test_lists_clients_in_code_order(self):
        Client.objects.create(**{**CLIENT, "codeClient": "C002"})
        Client.objects.create(**{**CLIENT, "codeClient": "C001"})

        response = self.client.get(self.url)

        self.assertEqual(
            [row["codeClient"] for row in response.json()], ["C001", "C002"])

    def test_creates_a_client(self):
        response = self.client.post(self.url, CLIENT, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Client.objects.count(), 1)
        self.assertEqual(Client.objects.get().nomPrenomClient, "Ada Lovelace")

    def test_rejects_a_client_without_a_code(self):
        payload = {key: value for key, value in CLIENT.items()
                   if key != "codeClient"}

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("codeClient", response.json())
