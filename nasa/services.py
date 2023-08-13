import json
from datetime import datetime

import requests
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status

from nasa.models import NearEarthObject, TaskResult


class NasaDataService:
    """Service for working with data received via nasa api."""

    def __init__(
        self,
        start_date: datetime,
        end_date: datetime = None,
    ) -> None:
        self.start_date = start_date
        self.end_date = start_date if end_date is None else end_date

    def get_nasa_data(self, count: int = None) -> dict[str, dict]:
        neo_data = self.__get_neo_data()
        if not neo_data:
            return

        parsed_neo_data = self.__parse_neo_data(neo_data)
        for neo in parsed_neo_data:
            self.__create_neo_in_db(neo)

        nasa_data = self.__get_neo_from_db(count)

        return nasa_data

    def __get_neo_data(self) -> dict[str, dict] | None:
        url = f'https://api.nasa.gov/neo/rest/v1/feed'\
              f'?start_date={self.start_date}&end_date={self.end_date}'\
              f'&api_key=DEMO_KEY'
        response = requests.get(url)
        if response.status_code == status.HTTP_200_OK:
            neo_data = response.json()
            return neo_data

    def __parse_neo_data(self, neo_data: dict[str, dict]) -> list[dict]:
        data = []
        for date, asteroids in neo_data['near_earth_objects'].items():
            for asteroid in asteroids:
                asteroid_dict = {
                    'date': date,
                    'neo_reference_id': asteroid['neo_reference_id'],
                    'name': asteroid['name'],
                    'absolute_magnitude_h': asteroid['absolute_magnitude_h'],
                    'is_potentially_hazardous_asteroid': asteroid[
                        'is_potentially_hazardous_asteroid'
                    ]
                }
                data.append(asteroid_dict)
        return data

    def __create_neo_in_db(self, data: dict) -> NearEarthObject:
        neo, _ = NearEarthObject.objects.update_or_create(
            date=data['date'],
            neo_reference_id=data['neo_reference_id'],
            name=data['name'],
            absolute_magnitude_h=data['absolute_magnitude_h'],
            is_potentially_hazardous_asteroid=data[
                'is_potentially_hazardous_asteroid'
            ]
        )
        return neo

    def __get_neo_from_db(self, count: int = None) -> dict[str, dict]:
        unique_dates = NearEarthObject.objects.values_list('date').distinct()\
            .filter(date__range=[self.start_date, self.end_date])

        result = {}
        for date in unique_dates:
            asteroids_per_day = NearEarthObject.objects.values(
                    'date',
                    'neo_reference_id',
                    'name',
                    'absolute_magnitude_h',
                    'is_potentially_hazardous_asteroid'
                ).filter(date=date[0])\
                .order_by('date', '-absolute_magnitude_h')[:count]

            for asteroid in asteroids_per_day:
                result.update({
                    f"{asteroid['date']} {asteroid['neo_reference_id']}": {
                        'name': asteroid['name'],
                        'absolute_magnitude_h': asteroid[
                            'absolute_magnitude_h'
                        ],
                        'is_potentially_hazardous_asteroid': asteroid[
                            'is_potentially_hazardous_asteroid'
                        ]
                    }
                })

        return result


class TaskService:
    """Service for working with tasks to retrieve data from nasa api."""

    def __init__(
        self,
        start_date: datetime,
        end_date: datetime = None,
        count: int = None
    ) -> None:
        self.start_date = start_date
        self.end_date = start_date if end_date is None else end_date
        self.count = count

    def create_task(self) -> int | None:
        nasa_data = self.__get_nasa_data()
        task_id = self.__create_task_result_in_db(nasa_data)
        return task_id

    @staticmethod
    def get_task_result(task_id: int):
        try:
            result = TaskResult.objects.get(pk=task_id)
        except ObjectDoesNotExist as e:
            return {"error": f'{e}'}

        return json.loads(result.task_result)

    def __get_nasa_data(self) -> dict[str, dict]:
        nasa_service = NasaDataService(
            start_date=self.start_date,
            end_date=self.end_date
        )
        nasa_data = nasa_service.get_nasa_data(count=self.count)
        return nasa_data

    def __create_task_result_in_db(self, data: dict) -> int:
        task_result = json.dumps(data)
        result = TaskResult.objects.create(task_result=task_result)
        return result.pk
