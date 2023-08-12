import datetime
import json

import requests
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status

from nasa.models import NearEarthObject, TaskResult


def get_neo_data(
    start_date: datetime,
    end_date: datetime = None
) -> dict | None:
    if not end_date:
        end_date = start_date
    url = f'https://api.nasa.gov/neo/rest/v1/feed?start_date={start_date}&end_date={end_date}&api_key=DEMO_KEY'  # noqa
    response = requests.get(url)
    if response.status_code == status.HTTP_200_OK:
        neo_data = response.json()
        return neo_data


def parse_neo_data(neo_data: dict[str, dict]) -> list[dict]:
    data = []
    for date, asteroids in neo_data['near_earth_objects'].items():
        for asteroid in asteroids:
            asteroid_dict = {
                'date': date,
                'neo_reference_id': asteroid['neo_reference_id'],
                'name': asteroid['name'],
                'absolute_magnitude_h': asteroid['absolute_magnitude_h'],
                'is_potentially_hazardous_asteroid': asteroid['is_potentially_hazardous_asteroid']  # noqa
            }
            data.append(asteroid_dict)
    return data


def create_neo_in_db(data: dict) -> NearEarthObject:
    neo, _ = NearEarthObject.objects.update_or_create(
        date=data['date'],
        neo_reference_id=data['neo_reference_id'],
        name=data['name'],
        absolute_magnitude_h=data['absolute_magnitude_h'],
        is_potentially_hazardous_asteroid=data['is_potentially_hazardous_asteroid']  # noqa
    )
    return neo


def get_neo_from_db(
    start_date: datetime,
    end_date: datetime = None,
    count: int = None
) -> dict[str, dict]:
    if not end_date:
        end_date = start_date

    unique_dates = NearEarthObject.objects.values_list('date').distinct()\
        .filter(date__range=[start_date, end_date])

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
                    'absolute_magnitude_h': asteroid['absolute_magnitude_h'],
                    'is_potentially_hazardous_asteroid': asteroid['is_potentially_hazardous_asteroid']  # noqa
                }
            })

    return result


def create_task_result_in_db(data: dict) -> int:
    task_result = json.dumps(data)
    result = TaskResult.objects.create(task_result=task_result)
    return result.pk


def create_task(
    start_date: datetime,
    end_date: datetime = None,
    count: int = None
) -> int | None:
    neo_data = get_neo_data(start_date, end_date)
    if not neo_data:
        return

    parsed_neo_data = parse_neo_data(neo_data)
    for neo in parsed_neo_data:
        create_neo_in_db(neo)

    neo_data_from_db = get_neo_from_db(
        start_date=start_date,
        end_date=end_date,
        count=count
    )
    task_id = create_task_result_in_db(neo_data_from_db)

    return task_id


def get_task_result(task_id: int):
    try:
        result = TaskResult.objects.get(pk=task_id)
    except ObjectDoesNotExist as e:
        return {"error": f'{e}'}

    return json.loads(result.task_result)
