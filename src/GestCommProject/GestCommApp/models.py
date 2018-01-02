from django.db import models

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

    def __init__(self, codeClient):
        self.codeClient = codeClient

    def __str(self):
        return '%d: %s' % (self.idClient, self.codeClient)

    class Meta:
        db_table = "client"
        unique_together = ('idClient', 'codeClient')
        ordering = ['codeClient']

# ManyToManyField = models.ManyToManyField(Group)
# ManyToManyField = models.ManyToManyField(User)
