from django.contrib import admin

from .models import Intension, Mystery, Person, PersonIntension

admin.site.register(Intension)
admin.site.register(Person)
admin.site.register(Mystery)


class PersonIntensionAdmin(admin.ModelAdmin):
    exclude = ('code', 'downloaded',)

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


admin.site.register(PersonIntension, PersonIntensionAdmin)
