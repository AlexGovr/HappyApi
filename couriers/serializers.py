from time import strptime, strftime
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Courier, Order


class CustomTimeSerializer(serializers.ModelSerializer):

    time_field_name = ''

    def __init__(self, *args, **kwargs):
        '''assign proper name for time_field validation method'''
        field_name = self.__class__.time_field_name
        validation_method_name = f'validate_{field_name}'
        setattr(self, validation_method_name, self._validate_time)
        super().__init__(*args, **kwargs)

    def to_internal_value(self, data):
        '''transform time intervals list to a comma-separated string'''
        whours = data.get(self.time_field_name, None)
        if whours:
            # raise if not list
            if not isinstance(whours, list):
                raise serializers.ValidationError(f'{self.time_field_name} values intervals'
                                                    'must be contained in a list')
            data[self.time_field_name] = ','.join(whours)
        return super().to_internal_value(data)

    def to_representation(self, inst):
        '''transform time intervals str to list'''
        data = super().to_representation(inst)
        whours = data[self.time_field_name]
        data[self.time_field_name] = whours.split(',')
        return data

    def _validate_time(self, value):
        '''validate time string by simply parsing it'''
        try:
            _time = [parse_timeint(t) for t in value.split(',')]
        except ValueError as e:
            raise ValidationError(detail=str(e))
        _str_list = [srl_timeint(*t) for t in _time]
        _str = ','.join(_str_list)
        return _str

class CourierSerializer(CustomTimeSerializer):

    time_field_name = 'working_hours'

    class Meta:
        model = Courier
        fields = '__all__'


class OrderSerializer(CustomTimeSerializer):

    time_field_name = 'delivery_hours'

    class Meta:
        model = Order
        fields = ['order_id', 'delivery_hours', 'region', 'weight']


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