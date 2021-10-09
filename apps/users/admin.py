from django.contrib import admin
from apps.users.models import *

admin.site.register(User)
admin.site.register(BudgetTariff)
admin.site.register(BudgetFillHistory)
admin.site.register(CashbackHistory)
admin.site.register(InvitedUser)
admin.site.register(FreeItem)
admin.site.register(Point)
admin.site.register(UserNotification)





