from copy import deepcopy
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError, bad_request
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Courier, Order
from .time_parse import parse_datetime
from .serializers import CourierSerializer, OrderSerializer


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

    def update(self, request, *args, **kwargs):
        '''almost fully copied from the inherited class
        except orders validity check'''
        partial = kwargs.pop('partial', False)
        courier = self.get_object()
        # remember old courier object
        old = deepcopy(courier)
        serializer = self.get_serializer(instance=courier, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        # check orders are valid after courier is changed
        serializer.instance.perform_changes(old)

        if getattr(courier, '_prefetched_objects_cache', None):
            courier._prefetched_objects_cache = {}
        
        return Response(serializer.data)


class OrderViewset(BaseViewset):
    serializer_class = OrderSerializer
    queryset = Order.objects.filter(completed=False)
    id_fieldname = 'order_id'
    resp_data_key = 'orders'

    @action(methods=['POST'], detail=False, url_path='assign')
    def assign(self, request):
        courier_id = request.data['courier_id']
        cour_or_404 = get_or_400(Courier, courier_id=courier_id)
        if isinstance(cour_or_404, Response):
            return cour_or_404

        courier = cour_or_404
        active_orders = self.queryset.filter(completed=False, courier_id=courier_id)
        if active_orders:
            orders = active_orders
            assign_time = orders[0].assign_time
        else:
            orders, assign_time = courier.assign_orders(self.queryset)

        if assign_time is None:
            resp_data = {'orders': []}
        else:
            ids = [{'id': ordr.order_id} for ordr in orders]
            resp_data = {'orders': ids, 'assign_time': assign_time}

        return Response(resp_data, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False, url_path='complete')
    def complete(self, request):
        courier_id = request.data['courier_id']
        order_id = request.data['order_id']
        complete_time = request.data['complete_time']
        
        order = get_or_400(Order, order_id=order_id)
        if isinstance(order, Response):
            return order

        courier = get_or_400(Courier, courier_id=courier_id)
        if isinstance(courier, Response):
            return courier

        if order.courier_id is None:
            return resp400('order is not assigned')
        if order.courier_id != courier:
            return resp400('order is assigned to another courier')

        complete_time = parse_datetime(complete_time)
        order.set_complete(courier, complete_time)

        resp_data = {'order_id': order_id}
        return Response(resp_data, status=status.HTTP_200_OK)


def get_or_400(model, **kwargs):
    try:
        inst = model.objects.get(**kwargs)
        return inst
    except ObjectDoesNotExist:
        name = model.__name__.lower()
        fieldnames = ', '.join(kwargs.keys())
        resp_data = {'detail': f'no {name} with such [{fieldnames}] fields'}
        return Response(resp_data, status=status.HTTP_400_BAD_REQUEST)


def resp400(detail):
    return Response({'detail': detail}, status=status.HTTP_400_BAD_REQUEST)
