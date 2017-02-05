from django.contrib import admin

from .models import Intension, Mystery, Person, PersonIntension
from django.utils import formats

admin.site.register(Mystery)

class PersonAdmin(admin.ModelAdmin):
    exclude = ('last_activity',)

admin.site.register(Person, PersonAdmin)

class PersonIntensionAdmin(admin.ModelAdmin):
    exclude = ('code', 'downloaded',)
    list_display = ('get_pi_details',)
    ordering = ('-intension__start_date',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'mystery':
            kwargs['queryset'] = Mystery.objects.order_by('number')
        if db_field.name == 'intension':
            from django.utils.datetime_safe import datetime as django_datetime
            import datetime
            days_31_ago = django_datetime.today() - datetime.timedelta(days=31)
            kwargs['queryset'] = Intension.objects.filter(start_date__gte=days_31_ago).order_by('start_date')
        if db_field.name == 'person':
            kwargs['queryset'] = Person.objects.order_by('name')
        return super(PersonIntensionAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_pi_details(self, obj):
        return formats.date_format(obj.intension.start_date, 'Y-m')  + " [" + obj.mystery.number_group() + "] " + obj.person.name


admin.site.register(PersonIntension, PersonIntensionAdmin)


class IntensionAdmin(admin.ModelAdmin):
    exclude = ('evangelisation_intension',)


admin.site.register(Intension, IntensionAdmin)
