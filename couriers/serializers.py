from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework.fields import empty
from rest_framework.exceptions import ValidationError
from .models import Courier, Order
from .time_parse import parse_timeint, srl_timeint


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
            # raise if not in list
            if not isinstance(whours, list):
                s = (f'{self.time_field_name} values intervals '
                     + 'must be contained in a list')
                raise serializers.ValidationError(s)
            data[self.time_field_name] = ','.join(whours)
        try:
            return super().to_internal_value(data)
        except ValidationError as e:
            # return data back to list form
            # to prevent further validation error
            data[self.time_field_name] = whours
            raise e

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
        self.check_time_intervals(_time)
        _str_list = [srl_timeint(*t) for t in _time]
        _str = ','.join(_str_list)
        return _str

    def run_validation(self, data=empty):
        """
        override to handle custom error
        """
        (is_empty_value, data) = self.validate_empty_values(data)
        if is_empty_value:
            return data

        try:
            # put this row under try-except to handle
            # "working_hours field must be contained in a list" error
            value = self.to_internal_value(data)
            self.run_validators(value)
            value = self.validate(value)
            assert (value is not None,
                    '.validate() should return the validated data')
        except (ValidationError, DjangoValidationError) as exc:
            raise ValidationError(detail=serializers.as_serializer_error(exc))

        return value

    def check_time_intervals(self, intvs):
        for b, e in intvs:
            if b >= e:
                raise ValidationError('working_hours beginning '
                                      'must be greater than ending')


class CourierSerializer(CustomTimeSerializer):

    time_field_name = 'working_hours'

    class Meta:
        model = Courier
        exclude = ['earnings', 'earning_ratio', ]


class OrderSerializer(CustomTimeSerializer):

    time_field_name = 'delivery_hours'

    class Meta:
        model = Order
        fields = ['order_id', 'delivery_hours', 'region', 'weight', ]
