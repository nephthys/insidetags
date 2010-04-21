from django.contrib import admin
from django.contrib.flatpages.admin import FlatPageAdmin as StockFlatPageAdmin
from models import *

class ExtendPageInline(admin.StackedInline):
    model = ExtendPage

class FlatPageAdmin(StockFlatPageAdmin):
    inlines = [ExtendPageInline]

admin.site.unregister(FlatPage)
admin.site.register(FlatPage, FlatPageAdmin)