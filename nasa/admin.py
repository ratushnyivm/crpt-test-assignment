from django.contrib import admin

from nasa import models


@admin.register(models.NearEarthObject)
class NearEarthObjectAdmin(admin.ModelAdmin):
    list_display = (
        'date',
        'neo_reference_id',
        'name',
        'absolute_magnitude_h',
        'is_potentially_hazardous_asteroid'
    )


@admin.register(models.TaskResult)
class TaskResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'task_result')
