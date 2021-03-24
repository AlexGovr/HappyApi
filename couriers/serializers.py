from time import strptime, strftime
from rest_framework import serializers
from .models import Courier


class CourierSerializer(serializers.ModelSerializer):

    working_hours = serializers.CharField(required=True)

    class Meta:
        model = Courier
        fields = '__all__'

    def to_internal_value(self, data):
        whours = data['working_hours']
        if not isinstance(whours, list):
            raise serializers.ValidationError('working hours intervals must be contained in a list')
        data['working_hours'] = ','.join(whours)
        return super().to_internal_value(data)

    def to_representation(self, inst):
        data = super().to_representation(inst)
        whours = data['working_hours']
        data['working_hours'] = whours.split(',')
        return data

    def validate_working_hours(self, value):
        _time = [parse_timeint(t) for t in value.split(',')]
        _str_list = [srl_timeint(*t) for t in _time]
        _str = ','.join(_str_list)
        return _str


def parse_timeint(timeinterval):
    stamps = timeinterval.split('-')
    begin = parse_time(stamps[0])
    end = parse_time(stamps[1])
    return begin, end


def parse_time(time_str):
    return strptime(time_str, '%H:%M')


def srl_timeint(begin, end):
    return f'{srl_time(begin)}-{srl_time(end)}'


def srl_time(time):
    return strftime('%H:%M', time)