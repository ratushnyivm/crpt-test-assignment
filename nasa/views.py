from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from nasa import serializers, services


class TaskIdView(APIView):
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = serializers.TaskResultSerializer(
            data=request.query_params
        )
        serializer.is_valid(raise_exception=True)

        task_result = services.get_task_result(
            serializer.validated_data.get('task_id')
        )

        return Response(task_result)


class FormIdView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'form_get_task_id.html'

    def get(self, request):
        serializer = serializers.TaskIdSerializer
        return Response({'serializer': serializer})


class FormResultView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'form_get_task_result.html'

    def get(self, request):
        serializer = serializers.TaskResultSerializer
        return Response({'serializer': serializer})
