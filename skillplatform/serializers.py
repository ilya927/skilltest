from rest_framework import serializers


class AIRequestSerializer(serializers.Serializer):
    text = serializers.CharField()
    subject = serializers.CharField(required=False, default="general")
    difficulty = serializers.CharField(required=False, default="medium")