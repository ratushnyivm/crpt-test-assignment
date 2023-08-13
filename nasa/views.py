from rest_framework import permissions, renderers, response, status, views

from nasa import serializers, services


class TaskIdView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = serializers.TaskIdSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        task = services.TaskService(
            start_date=serializer.validated_data.get('start_date'),
            end_date=serializer.validated_data.get('end_date'),
            count=serializer.validated_data.get('count')
        )
        task_id = task.create_task()

        if task_id is None:
            return response.Response(
                {'error': 'Failed to retrieve data from nasa. Try again.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return response.Response({'task_id': task_id})


class TaskResultView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = serializers.TaskResultSerializer(
            data=request.query_params
        )
        serializer.is_valid(raise_exception=True)

        task_result = services.TaskService.get_task_result(
            task_id=serializer.validated_data.get('task_id')
        )

        if task_result.get('error'):
            return response.Response(
                task_result,
                status=status.HTTP_404_NOT_FOUND
            )

        return response.Response(task_result)


class FormIdView(views.APIView):
    renderer_classes = [renderers.TemplateHTMLRenderer]
    template_name = 'form_get_task_id.html'

    def get(self, request):
        serializer = serializers.TaskIdSerializer
        return response.Response({'serializer': serializer})


class FormResultView(views.APIView):
    renderer_classes = [renderers.TemplateHTMLRenderer]
    template_name = 'form_get_task_result.html'

    def get(self, request):
        serializer = serializers.TaskResultSerializer
        return response.Response({'serializer': serializer})
