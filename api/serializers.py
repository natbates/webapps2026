from rest_framework import serializers


class ConversionSerializer(serializers.Serializer):
    rate = serializers.FloatField()
    converted_amount = serializers.FloatField()
