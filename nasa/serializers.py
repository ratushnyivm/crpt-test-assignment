from rest_framework import serializers


class TaskIdSerializer(serializers.Serializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField(required=False)
    count = serializers.IntegerField(min_value=1, required=False)

    def validate(self, attrs):
        if attrs.get('end_date') and attrs['start_date'] > attrs['end_date']:
            raise serializers.ValidationError(
                {"end_date": "End date must be after start date."}
            )
        return attrs


class TaskResultSerializer(serializers.Serializer):
    task_id = serializers.IntegerField(min_value=1)
