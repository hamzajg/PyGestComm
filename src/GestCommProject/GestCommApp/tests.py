from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from GestCommApp.models import Article, Client, Devis, Facture

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


class AssistantApiTest(APITestCase):
    url = "/api/assistant/ask"

    def setUp(self):
        Client.objects.create(**CLIENT)
        Client.objects.create(**{**CLIENT,
                                 "codeClient": "C002",
                                 "nomPrenomClient": "Grace Hopper",
                                 "numTelClient1": 33333333,
                                 "numTelClient2": 44444444})

    def ask(self, question):
        return self.client.post(self.url, {"question": question}, format="json")

    def test_count_intent(self):
        response = self.ask("how many clients?")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response.json()
        self.assertEqual(body["intent"], "count")
        self.assertEqual(body["data"]["count"], 2)

    def test_search_by_code(self):
        body = self.ask("find client C002").json()
        self.assertEqual(body["intent"], "search")
        self.assertEqual(len(body["data"]["clients"]), 1)
        self.assertEqual(body["data"]["clients"][0]["codeClient"], "C002")

    def test_search_by_name(self):
        body = self.ask("find client hopper").json()
        self.assertEqual(body["intent"], "search")
        self.assertEqual(body["data"]["clients"][0]["nomPrenomClient"], "Grace Hopper")

    def test_bare_term_searches(self):
        body = self.ask("Ada Lovelace").json()
        self.assertEqual(body["intent"], "search")
        self.assertEqual(body["data"]["clients"][0]["codeClient"], "C001")

    def test_search_by_phone(self):
        body = self.ask("find client 33333333").json()
        self.assertEqual(body["data"]["clients"][0]["codeClient"], "C002")

    def test_unknown_question_falls_back_to_search_or_help(self):
        response = self.ask("xyzzy")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(response.json()["intent"], ("search", "help"))

    def test_empty_question_is_help(self):
        body = self.ask("").json()
        self.assertEqual(body["intent"], "help")


ARTICLE = {
    "refArticle": "ART-001",
    "descArticle": "Widget",
    "prixAchatUnitaire": "50.00",
    "remiseAchat": 0,
    "tvaAchat": 20,
    "prixVenteUnitaire": "100.00",
    "remiseVente": 0,
    "tvaVente": 20,
    "dernierPrixVenteUnitaire": "100.00",
}

DEVIS = {
    "codeDevis": "D001",
    "dateDevis": "2026-11-17",
    "statutDevis": "brouillon",
    "observationDevis": "Test quote",
}

FACTURE = {
    "codeFacture": "F001",
    "dateFacture": "2026-11-17",
    "statutFacture": "brouillon",
    "observationFacture": "Test invoice",
}


class ArticleApiTest(APITestCase):
    url = "/api/article"

    def test_creates_and_retrieves_an_article(self):
        response = self.client.post(self.url, ARTICLE, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["refArticle"], "ART-001")

        detail = self.client.get(self.url + "/1")
        self.assertEqual(detail.status_code, status.HTTP_200_OK)
        self.assertEqual(detail.json()["descArticle"], "Widget")

    def test_updates_and_deletes_an_article(self):
        self.client.post(self.url, ARTICLE, format="json")

        response = self.client.patch(
            self.url + "/1", {"prixVenteUnitaire": "120.00"},
            format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Article.objects.get().prixVenteUnitaire, 120)

        response = self.client.delete(self.url + "/1")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Article.objects.count(), 0)


class ClientDetailApiTest(APITestCase):
    url = "/api/client"

    def setUp(self):
        Client.objects.create(**CLIENT)

    def test_retrieves_updates_and_deletes_a_client(self):
        response = self.client.get(self.url + "/1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["nomPrenomClient"], "Ada Lovelace")

        response = self.client.patch(
            self.url + "/1", {"nomPrenomClient": "A. Lovelace"},
            format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Client.objects.get().nomPrenomClient, "A. Lovelace")

        response = self.client.delete(self.url + "/1")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Client.objects.count(), 0)


class DevisApiTest(APITestCase):
    url = "/api/devis"

    def setUp(self):
        self.client_obj = Client.objects.create(**CLIENT)
        self.article = Article.objects.create(**{
            **ARTICLE,
            "prixVenteUnitaire": "100.00",
            "tvaVente": 20,
        })

    def test_creates_a_devis_with_article_lines_and_totals(self):
        payload = {
            **DEVIS,
            "client": self.client_obj.idClient,
            "lignes": [{"article": self.article.idArticle, "quantite": 2}],
        }
        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        body = response.json()
        self.assertEqual(body["codeClient"], "C001")
        self.assertEqual(len(body["lignes"]), 1)
        line = body["lignes"][0]
        self.assertEqual(line["designation"], "Widget")
        self.assertEqual(line["prixUnitaire"], "100.00")
        self.assertEqual(line["totalHT"], 200)
        self.assertEqual(body["totalHT"], 200)
        self.assertEqual(body["totalTVA"], 40)
        self.assertEqual(body["totalTTC"], 240)

    def test_creates_a_devis_with_a_free_text_line(self):
        payload = {
            **DEVIS,
            "client": self.client_obj.idClient,
            "lignes": [{
                "designation": "Prestation",
                "quantite": 1,
                "prixUnitaire": "50.00",
                "tva": 10,
            }],
        }
        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        body = response.json()
        self.assertEqual(body["totalHT"], 50)
        self.assertEqual(body["totalTVA"], 5)
        self.assertEqual(body["totalTTC"], 55)

    def test_rejects_a_line_without_designation_or_price(self):
        payload = {
            **DEVIS,
            "client": self.client_obj.idClient,
            "lignes": [{"quantite": 1}],
        }
        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Devis.objects.count(), 0)

    def test_updates_lines_and_status(self):
        payload = {
            **DEVIS,
            "client": self.client_obj.idClient,
            "lignes": [{"article": self.article.idArticle, "quantite": 1}],
        }
        self.client.post(self.url, payload, format="json")

        response = self.client.patch(
            self.url + "/1",
            {"statutDevis": "valide",
             "lignes": [{"designation": "Autre", "quantite": 3,
                         "prixUnitaire": "10.00", "tva": 0}]},
            format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response.json()
        self.assertEqual(body["statutDevis"], "valide")
        self.assertEqual(body["totalHT"], 30)
        self.assertEqual(len(body["lignes"]), 1)
        self.assertEqual(body["lignes"][0]["designation"], "Autre")

class FactureApiTest(APITestCase):
    url = "/api/facture"

    def setUp(self):
        self.client_obj = Client.objects.create(**CLIENT)
        self.article = Article.objects.create(**ARTICLE)
        self.devis = Devis.objects.create(
            **{**DEVIS, "client": self.client_obj})

    def test_creates_a_facture_linked_to_a_devis(self):
        payload = {
            **FACTURE,
            "client": self.client_obj.idClient,
            "devis": self.devis.idDevis,
            "lignes": [{"article": self.article.idArticle, "quantite": 1}],
        }
        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        body = response.json()
        self.assertEqual(body["codeDevis"], "D001")
        self.assertEqual(body["totalTTC"], 120)

    def test_lists_factures_and_updates_status(self):
        Facture.objects.create(**{**FACTURE, "client": self.client_obj})

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

        response = self.client.patch(
            self.url + "/1", {"statutFacture": "payee"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["statutFacture"], "payee")


class AssistantDomainApiTest(APITestCase):
    url = "/api/assistant/ask"

    def setUp(self):
        client_obj = Client.objects.create(**CLIENT)
        article = Article.objects.create(**ARTICLE)
        devis = Devis.objects.create(**{**DEVIS, "client": client_obj})
        Facture.objects.create(**{**FACTURE, "client": client_obj,
                                  "devis": devis})
        self.article = article

    def ask(self, question):
        return self.client.post(self.url, {"question": question},
                                format="json")

    def test_count_articles(self):
        body = self.ask("how many articles?").json()
        self.assertEqual(body["intent"], "count")
        self.assertEqual(body["data"]["resource"], "article")
        self.assertEqual(body["data"]["count"], 1)

    def test_count_devis_and_factures(self):
        self.assertEqual(
            self.ask("combien de devis").json()["data"]["count"], 1)
        self.assertEqual(
            self.ask("how many invoices").json()["data"]["count"], 1)

    def test_search_article_by_ref(self):
        body = self.ask("find article ART-001").json()
        self.assertEqual(body["intent"], "search")
        self.assertEqual(body["data"]["resource"], "article")
        self.assertEqual(body["data"]["articles"][0]["refArticle"], "ART-001")

    def test_search_devis_by_code(self):
        body = self.ask("find devis D001").json()
        self.assertEqual(body["data"]["resource"], "devis")
        self.assertEqual(body["data"]["devis"][0]["codeDevis"], "D001")

    def test_search_facture_by_linked_devis_code(self):
        body = self.ask("find facture D001").json()
        self.assertEqual(body["data"]["resource"], "facture")
        self.assertEqual(body["data"]["factures"][0]["codeFacture"], "F001")
