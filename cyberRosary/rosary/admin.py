from django.contrib import admin

# Register your models here.

from .models import Intension, Mystery, Person, PersonIntension

admin.site.register(Intension)
admin.site.register(Person)
admin.site.register(Mystery)

class PersonIntensionAdmin(admin.ModelAdmin):
    exclude = ('code', 'downloaded',)
admin.site.register(PersonIntension, PersonIntensionAdmin)
