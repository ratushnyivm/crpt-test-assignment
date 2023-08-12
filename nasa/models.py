from django.db import models


class NearEarthObject(models.Model):
    date = models.DateField()
    neo_reference_id = models.CharField()
    name = models.CharField()
    absolute_magnitude_h = models.FloatField()
    is_potentially_hazardous_asteroid = models.BooleanField()

    def __str__(self) -> str:
        return f'{self.date} {self.neo_reference_id}'


class TaskResult(models.Model):
    task_result = models.TextField()
