from django.contrib import admin
from paymentServicesApp.models import *

admin.site.register(PremiumsModel)
admin.site.register(PayMethodsModel)
admin.site.register(SubscriptionsModel)
admin.site.register(UserPaymentsHistoryModel)
admin.site.register(PremiumsOwnersModel)
admin.site.register(PremiumsGuestsModel)