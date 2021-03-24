from rest_framework import status, viewsets
from rest_framework.response import Response
from .serializers import CourierSerializer
from .models import Courier


class CourierViewset(viewsets.ModelViewSet):

    serializer_class = CourierSerializer
    queryset = Courier.objects.all()

    def create(self, request, *args, **kwargs):
        data = request.data['data']
        serializer = self.get_serializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
