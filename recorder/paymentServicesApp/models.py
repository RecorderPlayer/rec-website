from django.db import models


class PremiumsModel(models.Model):
    """
    Create a Premiums table for the database
    """
    user = models.ForeignKey('authApp.UsersModel', on_delete=models.CASCADE, default=None, null=True)
    owner = models.ForeignKey('paymentServicesApp.PremiumsOwnersModel', on_delete=models.CASCADE, null=True, blank=True)
    guest = models.ForeignKey('paymentServicesApp.PremiumsGuestsModel', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = "Premium Main"

    def __str__(self):
        return str(self.user)


class PremiumsGuestsModel(models.Model):
    """
        Model for users who was invited to already created premium model
    """
    core_premium = models.ForeignKey('paymentServicesApp.PremiumsOwnersModel', on_delete=models.CASCADE, verbose_name='Core premium model')
    join_at = models.DateTimeField(verbose_name='Was join to premium at')
    user = models.ForeignKey('authApp.UsersModel', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Premium Guest'

    def __str__(self):
        return str(self.user) + ' | ' + str(self.core_premium)


class PremiumsOwnersModel(models.Model):
    """
        Creating model for users who want to buy premium
    """
    owner = models.ForeignKey('authApp.UsersModel', on_delete=models.CASCADE)
    activated_at = models.DateTimeField(default=None)
    price = models.DecimalField(max_digits=18, decimal_places=2)
    active = models.BooleanField(default=False)
    period = models.DateTimeField(default=None)
    method = models.ForeignKey('paymentServicesApp.PayMethodsModel', on_delete=models.CASCADE)
    subscription = models.ForeignKey('paymentServicesApp.SubscriptionsModel', on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Premium Owner"

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


class UserPaymentsHistoryModel(models.Model):
    """
        User Payments History table
    """

    account = models.ForeignKey('authApp.UsersModel', verbose_name='Account', on_delete=models.CASCADE)
    price = models.DecimalField(verbose_name='Price', max_digits=18, decimal_places=2)
    method = models.ForeignKey('paymentServicesApp.PayMethodsModel', verbose_name='Payment method', on_delete=models.CASCADE)
    subscription = models.ForeignKey('paymentServicesApp.SubscriptionsModel', default=None, null=True, blank=True, on_delete=models.CASCADE)
    song = models.ForeignKey('songsApp.SongsModel', null=True, blank=True, default=None, on_delete=models.CASCADE)
    made_at = models.DateTimeField(verbose_name='Was made at')
    wallet_from = models.CharField(verbose_name='From', max_length=42)
    wallet_to = models.CharField(verbose_name='To', max_length=42)
    hash = models.CharField(verbose_name='Hash', max_length=66)
    period = models.DateTimeField(default=None, null=True, blank=True)

    class Meta:
        verbose_name = 'UserPaymentsHistory'

    def __str__(self):
        return str(self.account) + ' ' + str(self.subscription if self.subscription is not None else self.song)


class SubscriptionsModel(models.Model):
    """
        Model with all types of subscription model
    """

    price = models.DecimalField(verbose_name='Price', max_digits=18, decimal_places=2)
    name = models.CharField(verbose_name='Name', max_length=64)
    count_of_users = models.IntegerField(verbose_name='Count of available users')
    description = models.TextField(verbose_name='Description')

    class Meta:
        verbose_name = 'Subscription'

    def __str__(self):
        return str(self.name)


