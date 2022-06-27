from django.db import models


class PremiumsModel(models.Model):
    """
    Create a Premiums table for the database
    """
    activated_at = models.DateTimeField(default=None)
    price = models.FloatField()
    active = models.BooleanField(default=False)
    period = models.DateTimeField(default=None)
    method = models.ForeignKey("paymentServicesApp.PayMethodsModel", on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = "Premium"

    def __str__(self):
        return str(self.id)


class PayMethodsModel(models.Model):
    """
    Create a PayMethods table for the database
    """

    name = models.CharField(max_length=32)

    class Meta:
        verbose_name = "PayMethod"

    def __str__(self):
        return str(self.name)
