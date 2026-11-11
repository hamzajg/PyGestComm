from django.test import TestCase

from GestCommApp.models import Client


class ClientModelTests(TestCase):
    def test_create_client(self):
        client = Client.objects.create(
            codeClient="C001",
            nomPrenomClient="Ada Lovelace",
            matFiscalClient="1234567",
            addresseClient1="1 Analytical Engine Way",
            addresseClient2="Suite 2",
            numTelClient1=11111111,
            numTelClient2=22222222,
        )
        self.assertEqual(str(client), "%d: C001" % client.idClient)
