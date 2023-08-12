from rest_framework.response import Response
from rest_framework.views import APIView

from nasa import serializers, services


class TaskIdView(APIView):
    def get(self, request):
        serializer = serializers.TaskIdSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        task_id = services.create_task(
            start_date=serializer.validated_data.get('start_date'),
            end_date=serializer.validated_data.get('end_date'),
            count=serializer.validated_data.get('count')
        )

        if task_id is None:
            return Response(
                {'error': 'Failed to retrieve data from nasa. Try again.'}
            )

        return Response({'task_id': task_id})


class TaskResultView(APIView):
    def get(self, request):
        serializer = serializers.TaskResultSerializer(
            data=request.query_params
        )
        serializer.is_valid(raise_exception=True)

        task_result = services.get_task_result(
            serializer.validated_data.get('task_id')
        )

        return Response(task_result)
