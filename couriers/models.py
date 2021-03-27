from time import strptime, strftime
from datetime import datetime
from django.db import models


class Courier(models.Model):
    type_choices = [('foot', 'foot'), ('bike', 'bike'), ('car', 'car'),]
    courier_id = models.IntegerField(primary_key=True)
    courier_type = models.CharField(max_length=20, choices=type_choices, blank=False)
    regions = models.CharField(max_length=120, blank=False)
    working_hours = models.CharField(max_length=240, blank=False)

    payload_dict = {
        'foot': 10,
        'bike': 15,
        'car': 50,
    }

    @property
    def payload(self):
        return __class__.payload_dict[self.courier_type]

    def assign_orders(self, orders):
        assign_time = datetime.now()
        orders = self.filter_orders(orders)
        chosen = opt_byweight(orders, self.payload)
        if not chosen:
            return None, None
        for ordr in chosen:
            ordr.courier_id = self.courier_id
            ordr.assign_time = assign_time
            # ordr.save()
        assign_time = srl_time(assign_time)
        return chosen, assign_time

    def filter_orders(self, orders):
        orders = orders.filter(courier_id=None, weight_le=self.payload)
        orders = self.filter_by_time(orders)
        return orders

    def filter_by_time(self, orders):
        whours = [parse_timeint(tint) for tint in self.working_hours.split(',')]
        chosen = []
        for ordr in orders:
            dhours = [parse_timeint(tint) for tint in ordr.delivery_hours.split(',')]
            for wbegin, wend in whours:
                for dbegin, dend in dhours:
                    if (wbegin < dbegin < wend
                        or wbegin < dend < wend):
                        chosen.append(ordr)
        return sorted(orders, reverse=True)


class Order(models.Model):
    order_id = models.IntegerField(primary_key=True)
    region = models.IntegerField(blank=False)
    weight = models.FloatField(blank=False)
    delivery_hours = models.CharField(max_length=240, blank=False)
    courier_id = models.ForeignKey(Courier, null=True, on_delete=models.SET_NULL)
    completed = models.BooleanField(default=False)
    assign_time = models.DateTimeField(null=True)
    complete_time = models.DateTimeField(null=True)


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
