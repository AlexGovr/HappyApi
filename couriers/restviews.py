from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from .serializers import CourierSerializer
from .models import Courier


class CourierViewset(viewsets.ModelViewSet):

    serializer_class = CourierSerializer
    queryset = Courier.objects.all()

    def create(self, request, *args, **kwargs):
        data = request.data['data']
        couriers = []
        allsrl = []
        for i, _dat in enumerate(data):
            srl = self.get_serializer(data=_dat)
            if srl.is_valid():
                print(srl.validated_data)
                allsrl.append(srl)
                couriers.append({'id': _dat['courier_id']})
            else:
                f_srl = self.get_serializer
                print(_dat['courier_id'], srl.data)
                errors = [{'id': _dat['courier_id']} for _dat in data[i:] if not f_srl(data=_dat).is_valid()]
                resp_data = {'validation_error':{'couriers': errors}}
                return Response(resp_data, status=status.HTTP_400_BAD_REQUEST)

        _ = [self.perform_create(srl) for srl in allsrl]
        headers = self.get_success_headers(allsrl[0].data)
        resp_data = {'couriers': couriers}
        return Response(resp_data, status=status.HTTP_201_CREATED, headers=headers)
