from datetime import datetime
from django.db import models
from .time_parse import (parse_timeint, parse_time, datetime_now,
                            srl_timeint, srl_time)


class Courier(models.Model):
    type_choices = [('foot', 'foot'), ('bike', 'bike'), ('car', 'car'),]
    ern_ft = 2
    ern_bk = 5
    ern_cr = 9
    earnratio_choices = [(ern_ft, 'foot'), (ern_bk, 'bike'), (ern_cr, 'car'),]

    courier_id = models.IntegerField(primary_key=True)
    courier_type = models.CharField(max_length=20, choices=type_choices, blank=False)
    regions = models.CharField(max_length=120, blank=False)
    working_hours = models.CharField(max_length=240, blank=False)
    earnings = models.FloatField(default=0)
    earning_ratio = models.IntegerField(choices=earnratio_choices, default=ern_ft)

    payload_dict = {
        'foot': 10,
        'bike': 15,
        'car': 50,
    }
    earnratio_dict = {
        'foot': ern_ft,
        'bike': ern_bk,
        'car': ern_cr,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.whours = [parse_timeint(tint) for tint
                        in self.working_hours.split(',')]

    @property
    def payload(self):
        return __class__.payload_dict[self.courier_type]

    def assign_orders(self, orders, use_my=False):
        assign_time = datetime_now()
        courier_id = None
        if use_my:
            courier_id = self

        orders = self.filter_orders(orders, courier_id=courier_id)
        orders = sorted(orders, reverse=True)
        _, chosen = opt_byweight(orders, self.payload)
        if not chosen:
            return [], None
        for ordr in chosen:
            ordr.courier_id = self
            ordr.assign_time = assign_time
            ordr.save()
        return chosen, assign_time

    def filter_orders(self, orders, courier_id=None):
        orders = orders.filter(courier_id=courier_id, weight__lte=self.payload)
        orders = self.filter_byregions(orders)
        orders = self.filter_by_time(orders)
        return orders

    def filter_byregions(self, orders):
        ints = map(int, self.regions.split(','))
        regions = set(ints)
        orders = [ordr for ordr in orders 
                    if ordr.region in regions]
        return orders

    def filter_by_time(self, orders):
        orders = [ordr for ordr in orders
                    if ordr._fits_schedule(self.whours)]
        return orders

    def perform_changes(self, prev):
        if (self.working_hours != prev.working_hours
                or self.regions != prev.regions
                or self.payload < prev.payload):
            orders = Order.objects.filter(courier_id=self.courier_id, completed=False)
            _orders, _ = self.assign_orders(orders, use_my=True)
            # set lost orders unassigned
            for ordr in orders:
                if ordr not in _orders:
                    ordr.courier_id = None
                    ordr.assign_time = None
                    ordr.save()


class Order(models.Model):
    order_id = models.IntegerField(primary_key=True)
    region = models.IntegerField(blank=False)
    weight = models.FloatField(blank=False)
    delivery_hours = models.CharField(max_length=240, blank=False)
    courier_id = models.ForeignKey(Courier, null=True, on_delete=models.SET_NULL)
    completed = models.BooleanField(default=False)
    assign_time = models.DateTimeField(null=True)
    complete_time = models.DateTimeField(null=True)
    deliviery_time = models.IntegerField(blank=True, default=0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dhours = [parse_timeint(tint) for tint
                        in self.delivery_hours.split(',')]

    def _fits_schedule(self, whours):
        for b, e in whours:
            if self._fits_timeint(b, e):
                return True
        return False

    def _fits_timeint(self, b, e):
        for dbegin, dend in self.dhours:
            if (e <= dbegin) or (dend <= b):
                continue
            return True
        return False

    def set_complete(self, courier, complete_time):
        self.courier_id = courier
        self.complete_time = complete_time
        self.completed = True
        self.save()
    
    def __lt__(self, order):
        return self.weight < order.weight
    
    def __gt__(self, order):
        return self.weight > order.weight


def opt_byweight(orders, sm):
    '''recursively packs list with orders to provide
    total weight closest to (but <= ) sm value'''
    # init iteration
    max_sm = 0
    max_arr = []
    # don't use overweighted orders
    orders = list(filter(lambda ordr: ordr.weight <= sm, orders))
    for i, ordr in enumerate(orders):
        # get the most optimized pack from further iteration
        _add, _orders = opt_byweight(orders[i+1:], sm - ordr.weight)
        _sm = ordr.weight + _add
        # fits perfectly! return
        if _sm == sm:
            return _sm, [ordr] + _orders
        # not perfect but better than all previous, remember
        if max_sm < _sm:
            max_sm = _sm
            max_arr = [ordr] + _orders
    return max_sm, max_arr
