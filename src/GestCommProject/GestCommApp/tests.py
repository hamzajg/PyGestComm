from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from GestCommApp.models import Article, BonLiv, Client, Devis, Facture

CLIENT = {
    "codeClient": "C001",
    "nomPrenomClient": "Ada Lovelace",
    "matFiscalClient": "1234567",
    "addresseClient1": "1 Analytical Engine Way",
    "addresseClient2": "Suite 2",
    "numTelClient1": 11111111,
    "numTelClient2": 22222222,
}



class AuthAPITestCase(APITestCase):
    """Every /api/* endpoint now requires authentication (ADR 0006);
    tests authenticate as a regular user."""

    def setUp(self):
        # No password: force_authenticate ignores it, and skipping the
        # hash keeps the suite fast (PBKDF2 ~1s per create_user).
        self.user = User.objects.create_user('api-user')
        self.client.force_authenticate(user=self.user)


class ClientModelTests(TestCase):
    def test_create_client(self):
        client = Client.objects.create(**CLIENT)

        self.assertEqual(str(client), "%d: C001" % client.idClient)


class ClientApiTest(AuthAPITestCase):
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


class AssistantApiTest(AuthAPITestCase):
    url = "/api/assistant/ask"

    def setUp(self):
        super().setUp()
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


class ArticleApiTest(AuthAPITestCase):
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


class ClientDetailApiTest(AuthAPITestCase):
    url = "/api/client"

    def setUp(self):
        super().setUp()
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


class DevisApiTest(AuthAPITestCase):
    url = "/api/devis"

    def setUp(self):
        super().setUp()
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

class FactureApiTest(AuthAPITestCase):
    url = "/api/facture"

    def setUp(self):
        super().setUp()
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


class AssistantDomainApiTest(AuthAPITestCase):
    url = "/api/assistant/ask"

    def setUp(self):
        super().setUp()
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


class DevisConversionApiTest(AuthAPITestCase):
    def setUp(self):
        super().setUp()
        self.client_obj = Client.objects.create(**CLIENT)
        self.article = Article.objects.create(**ARTICLE)
        self.devis = Devis.objects.create(
            **{**DEVIS, "client": self.client_obj,
               "statutDevis": "valide"})
        from GestCommApp.models import LigneDevis
        LigneDevis.objects.create(
            devis=self.devis, article=self.article, designation="Widget",
            quantite=2, prixUnitaire="100.00", remise=0, tva=20)

    def url(self, pk):
        return "/api/devis/%d/convertir" % pk

    def test_converts_a_validated_devis_into_a_facture(self):
        response = self.client.post(self.url(self.devis.idDevis), {},
                                    format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        body = response.json()
        self.assertEqual(body["codeFacture"], "F%04d" % self.devis.idDevis)
        self.assertEqual(body["codeDevis"], "D001")
        self.assertEqual(body["codeClient"], "C001")
        self.assertEqual(body["statutFacture"], "brouillon")
        self.assertEqual(body["totalHT"], 200)
        self.assertEqual(len(body["lignes"]), 1)
        self.assertEqual(body["lignes"][0]["designation"], "Widget")

        self.devis.refresh_from_db()
        self.assertEqual(self.devis.statutDevis, "converti")
        self.assertEqual(Facture.objects.count(), 1)

    def test_rejects_conversion_of_a_brouillon_devis(self):
        self.devis.statutDevis = "brouillon"
        self.devis.save()

        response = self.client.post(self.url(self.devis.idDevis), {},
                                    format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Facture.objects.count(), 0)

    def test_rejects_double_conversion(self):
        self.client.post(self.url(self.devis.idDevis), {}, format="json")
        response = self.client.post(self.url(self.devis.idDevis), {},
                                    format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Facture.objects.count(), 1)

    def test_unknown_devis_is_404(self):
        response = self.client.post(self.url(999), {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ListFilterApiTest(AuthAPITestCase):
    def setUp(self):
        super().setUp()
        self.client_obj = Client.objects.create(**CLIENT)
        other = Client.objects.create(**{
            **CLIENT, "codeClient": "C002",
            "nomPrenomClient": "Grace Hopper"})
        Article.objects.create(**ARTICLE)
        Article.objects.create(**{**ARTICLE, "refArticle": "ART-002",
                                  "descArticle": "Gadget"})
        Devis.objects.create(**{**DEVIS, "client": self.client_obj})
        Devis.objects.create(**{
            **DEVIS, "codeDevis": "D002", "client": other,
            "statutDevis": "valide"})
        Facture.objects.create(**{**FACTURE, "client": self.client_obj})

    def test_client_search_filter(self):
        response = self.client.get("/api/client?search=hopper")
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["codeClient"], "C002")

    def test_article_search_filter(self):
        response = self.client.get("/api/article?search=gadget")
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["refArticle"], "ART-002")

    def test_devis_statut_and_client_filters(self):
        response = self.client.get("/api/devis?statut=valide")
        self.assertEqual([d["codeDevis"] for d in response.json()], ["D002"])

        response = self.client.get(
            "/api/devis?client=%d" % self.client_obj.idClient)
        self.assertEqual([d["codeDevis"] for d in response.json()], ["D001"])

    def test_facture_search_filter_includes_devis_code(self):
        devis = Devis.objects.get(codeDevis="D002")
        Facture.objects.create(**{
            **FACTURE, "codeFacture": "F002", "client": devis.client,
            "devis": devis})

        response = self.client.get("/api/facture?search=D002")
        self.assertEqual(
            [f["codeFacture"] for f in response.json()], ["F002"])


class LockedDocumentApiTest(AuthAPITestCase):
    def setUp(self):
        super().setUp()
        self.client_obj = Client.objects.create(**CLIENT)
        self.facture = Facture.objects.create(
            **{**FACTURE, "client": self.client_obj,
               "statutFacture": "payee"})
        self.devis = Devis.objects.create(
            **{**DEVIS, "codeDevis": "D009", "client": self.client_obj,
               "statutDevis": "converti"})

    def test_payee_facture_rejects_patch_and_delete(self):
        response = self.client.patch(
            "/api/facture/%d" % self.facture.idFacture,
            {"observationFacture": "edit"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.delete(
            "/api/facture/%d" % self.facture.idFacture)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Facture.objects.count(), 1)

    def test_payee_facture_still_retrieves(self):
        response = self.client.get(
            "/api/facture/%d" % self.facture.idFacture)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_converti_devis_rejects_patch(self):
        response = self.client.patch(
            "/api/devis/%d" % self.devis.idDevis,
            {"observationDevis": "edit"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_brouillon_facture_still_updates(self):
        self.facture.statutFacture = "brouillon"
        self.facture.save()
        response = self.client.patch(
            "/api/facture/%d" % self.facture.idFacture,
            {"observationFacture": "ok"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ApiAuthTest(TestCase):
    """Auth is enforced at the DRF layer — these use a plain Client (no
    force_authenticate) to exercise real credential checks."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            'api-user', password='test-password')

    def test_unauthenticated_requests_are_rejected(self):
        for url in ('/api/client', '/api/article', '/api/devis',
                    '/api/facture', '/api/assistant/ask'):
            method = self.client.post if url.endswith('ask') else self.client.get
            response = method(url, {}, format='json') if url.endswith('ask') \
                else method(url)
            self.assertIn(response.status_code, (401, 403), url)

    def test_wrong_password_is_rejected(self):
        import base64
        token = base64.b64encode(b'api-user:wrong').decode()
        response = self.client.get(
            '/api/client', HTTP_AUTHORIZATION='Basic ' + token)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_basic_auth_grants_access(self):
        import base64
        token = base64.b64encode(b'api-user:test-password').decode()
        response = self.client.get(
            '/api/client', HTTP_AUTHORIZATION='Basic ' + token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


BONLIV = {
    "codeBonLiv": "BL001",
    "dateBonLiv": "2026-11-17",
    "statutBonLiv": "brouillon",
    "observationBonLiv": "Test delivery note",
}


class BonLivApiTest(AuthAPITestCase):
    url = "/api/bonliv"

    def setUp(self):
        super().setUp()
        self.client_obj = Client.objects.create(**CLIENT)
        self.article = Article.objects.create(**{
            **ARTICLE,
            "prixVenteUnitaire": "100.00",
            "tvaVente": 20,
        })

    def test_creates_a_bonliv_with_lines_and_totals(self):
        payload = {
            **BONLIV,
            "client": self.client_obj.idClient,
            "lignes": [{"article": self.article.idArticle, "quantite": 2}],
        }
        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        body = response.json()
        self.assertEqual(body["codeBonLiv"], "BL001")
        self.assertEqual(body["codeClient"], "C001")
        self.assertEqual(len(body["lignes"]), 1)
        self.assertEqual(body["lignes"][0]["designation"], "Widget")
        self.assertEqual(body["totalHT"], 200)
        self.assertEqual(body["totalTTC"], 240)

    def test_updates_statut_and_lists_with_filters(self):
        self.client.post(self.url, {
            **BONLIV,
            "client": self.client_obj.idClient,
            "lignes": [{"designation": "Colis", "quantite": 1,
                        "prixUnitaire": "10.00", "tva": 0}],
        }, format="json")

        response = self.client.patch(
            self.url + "/1", {"statutBonLiv": "valide"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["statutBonLiv"], "valide")

        listing = self.client.get(self.url + "?statut=valide")
        self.assertEqual(len(listing.json()), 1)
        self.assertEqual(
            self.client.get(self.url + "?statut=livre").json(), [])

    def test_livre_bonliv_rejects_patch_and_delete(self):
        self.client.post(self.url, {
            **BONLIV,
            "client": self.client_obj.idClient,
            "statutBonLiv": "livre",
        }, format="json")

        response = self.client.patch(
            self.url + "/1", {"observationBonLiv": "x"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            self.client.delete(self.url + "/1").status_code,
            status.HTTP_400_BAD_REQUEST)
        self.assertEqual(BonLiv.objects.count(), 1)


class AssistantBonLivApiTest(AuthAPITestCase):
    url = "/api/assistant/ask"

    def setUp(self):
        super().setUp()
        self.client_obj = Client.objects.create(**CLIENT)
        BonLiv.objects.create(
            codeBonLiv="BL009", client=self.client_obj,
            statutBonLiv="valide")

    def test_count_bons_de_livraison(self):
        response = self.client.post(
            self.url, {"question": "how many bons de livraison"},
            format="json")
        body = response.json()
        self.assertEqual(body["intent"], "count")
        self.assertEqual(body["data"]["count"], 1)
        self.assertEqual(body["data"]["resource"], "bonliv")

    def test_search_bonliv_by_code(self):
        response = self.client.post(
            self.url, {"question": "find bonliv BL009"}, format="json")
        body = response.json()
        self.assertEqual(body["intent"], "search")
        items = body["data"]["bons de livraison"]
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["codeBonLiv"], "BL009")
        self.assertEqual(items[0]["statutBonLiv"], "valide")
