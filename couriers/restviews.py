from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from .serializers import CourierSerializer, OrderSerializer
from .models import Courier, Order


class BaseViewset(viewsets.ModelViewSet):

    id_fieldname = ''
    resp_data_key = ''

    def __init__(self, *args, **kwargs):
        self.id_fieldname = self.__class__.id_fieldname
        self.error_data_key = self.__class__.resp_data_key
        super().__init__(*args, **kwargs)

    def create(self, request, *args, **kwargs):
        data = request.data['data']
        resp_ids = []
        allsrl = []
        for i, _dat in enumerate(data):
            srl = self.get_serializer(data=_dat)
            if srl.is_valid():
                allsrl.append(srl)
                resp_ids.append({'id': _dat[self.id_fieldname]})
            else:
                f_srl = self.get_serializer
                errors = [{'id': _dat[self.id_fieldname]}
                            for _dat in data[i:]
                            if not f_srl(data=_dat).is_valid()]
                resp_data = {'validation_error':{self.resp_data_key: errors}}
                return Response(resp_data, status=status.HTTP_400_BAD_REQUEST)

        _ = [self.perform_create(srl) for srl in allsrl]
        headers = self.get_success_headers(allsrl[0].data)
        resp_data = {self.resp_data_key: resp_ids}
        return Response(resp_data, status=status.HTTP_201_CREATED, headers=headers)


class CourierViewset(BaseViewset):
    serializer_class = CourierSerializer
    queryset = Courier.objects.all()
    id_fieldname = 'courier_id'
    resp_data_key = 'couriers'


class OrderViewset(BaseViewset):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    id_fieldname = 'order_id'
    resp_data_key = 'orders'
