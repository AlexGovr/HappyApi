from time import strptime
from rest_framework import serializers
from .models import Courier


class WrongTimeFormat(BaseException):
    pass


class CourierSerializer(serializers.ModelSerializer):

    class Meta:
        model = Courier
        fields = '__all__'

    def create(self, validated_data):
        working_hours = validated_data['working_hours']
        # check time format
        _ = [parse_time(t) for t in working_hours]


def parse_time_interval(timeinterval):
    stamps = timeinterval.split('-')
    if len(stamps) != 2:
        raise WrongTimeFormat()
    begin = parse_time(stamps[0])
    end = parse_time(stamps[1])
    return begin, end


def parse_time(time):
    try:
        return strptime(time, '%H:%M:%S')
    except:
        raise WrongTimeFormat()