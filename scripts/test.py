import requests
import datetime
from couriers.time_parse import parse_datetime

host = '178.154.195.226'


def srl_datetime(dt):
    return dt.strftime('%Y-%m-%dT%H:%M:%S.%f%z') + 'Z'


def tshift(dtime):
    def shift(minutes):
        '''shifts initial dtime by minutes 
        and returns new datetime object'''
        minutes += dtime.minute
        hours = minutes // 59 + dtime.hour
        minutes = minutes % 59
        return datetime.datetime(dtime.year, dtime.month, 
                                 dtime.day, minute=minutes, hour=hours)
    return shift


def test(descr, r, assrtto):
    print('\n', descr)
    check = r.status_code, r.reason
    assert check == assrtto, ((check, r.text), assrtto)
    print(r.text)
    return r.json()


def post_couriers(data):
    r = requests.post(f'http://{host}/couriers', json=data)
    return r


def patch_courier(data, _id):
    r = requests.patch(f'http://{host}/couriers/{_id}', json=data)
    return r


def post_orders(data):
    r = requests.post(f'http://{host}/orders', json=data)
    return r


def assign_orders(_id):
    r = requests.post(f'http://{host}/orders/assign', {'courier_id': _id})
    return r


def complete_order(cour_id, ord_id, t):
    t = srl_datetime(t)
    json = {
        'courier_id': cour_id,
        'order_id': ord_id,
        'complete_time': t
    }
    r = requests.post(f'http://{host}/orders/complete', json=json)
    return r


def get_courier(_id):
    r = requests.get(f'http://{host}/couriers/{_id}')
    return r


def delete_orders():
    r = requests.post(f'http://{host}/orders/deleteall')
    return r


def delete_couriers():
    r = requests.post(f'http://{host}/couriers/deleteall')
    return r


def create_order(*args):
    (_id,
    region,
    dhours,
    weight) = args
    return dict(order_id=_id, region=region, 
                delivery_hours=dhours, weight=weight)


def run():
    cour = {
        'courier_type': 'car', 
        'courier_id':0,
        'regions':'1,3,4',
        'working_hours':[
            '10:00-12:00',
            '13:00-14:00',
        ]
    }
    cour1 = {
        'courier_type': 'car', 
        'courier_id':1,
        'regions':'1,3,4',
        'working_hours':[
            '10:00-12:00',
            '13:00-14:00',
        ]
    }

    orders_data = [
        [0, 2, ['10:00-12:00', '13:00-14:00'], 5],
        [1, 5, ['10:00-12:00', '13:00-14:00'], 5],
        [2, 6, ['10:00-12:00', '13:00-14:00'], 5],

        [3, 1, ['09:00-10:00', '12:15-12:45'], 5],
        [4, 3, ['02:00-03:00', '15:00-15:15'], 5],
        [5, 4, ['02:00-03:00', '15:00-15:15'], 5],

        [6, 12, ['09:00-10:00', '12:15-12:45'], 5],
        [7, 5, ['02:00-03:00', '15:00-15:15'], 5],
        [8, 6, ['02:00-03:00', '15:00-15:15'], 5],

        [9, 1, ['10:00-12:00', '13:00-14:00'], 40],
        [10, 3, ['10:00-12:00', '13:00-14:00'], 35],
        [11, 4, ['10:00-12:00', '13:00-14:00'], 14],
        [12, 1, ['10:00-12:00', '12:30-13:30', '13:30-14:30'], 5],
        [13, 3, ['10:00-12:00', '13:00-14:00'], 4],
        [14, 4, ['10:00-10:05'], 3],
        [15, 1, ['10:00-12:00', '13:00-14:00'], 3],
        [16, 3, ['09:00-21:00'], 2],
        [17, 4, ['10:00-12:00', '13:00-14:00'], 2]
    ]

    additional_orders = [
        [18, 1, ['10:00-12:00', '13:00-14:00'], 25],
        [19, 3, ['10:00-12:00', '13:00-14:00'], 17],
        [20, 4, ['10:00-12:00', '13:00-14:00'], 10],
        [21, 1, ['10:00-12:00', '12:30-13:30', '13:30-14:30'], 1],
        [22, 3, ['10:00-12:00', '13:00-14:00'], 4],
    ]

    bad_orders = [
        [0, 2, '10:00-12:00,13:00-14:00', 5],
        [10, 3, ['10:00-12:00', '13:00-14:00'], -35],
        [11, 4, ['10:00-12:00', '13:00-14:'], 14],
        [11, 4, ['10:00-12:00', '17:00-14:00'], 14],
    ]

    delete_orders()
    delete_couriers()

    json = {'data': [cour, cour1]}
    test('post couriers', post_couriers(json), (201, 'Created'))

    test('patch courier 0', patch_courier(cour, 0), (200, 'OK'))
    test('patch courier 1', patch_courier(cour1, 1), (200, 'OK'))
    
    json = {'data':[create_order(*dat) for dat in orders_data]}
    test('post orders', post_orders(json), (201, 'Created'))

    json = {'data':[create_order(*dat) for dat in bad_orders]}
    test('post bad orders', post_orders(json), (400, 'Bad Request'))

    test('assign orders id=0', assign_orders(0), (200, 'OK'))
    json = {'courier_type': 'bike'}
    test('patch courier 0 to bike', patch_courier(json, 0), (200, 'OK'))

    data = test('assign orders id=0', assign_orders(0), (200, 'OK'))
    asgn_t = data['assign_time']
    shift = tshift(parse_datetime(asgn_t))

    test('assign orders id=1', assign_orders(1), (200, 'OK'))

    json={
        'courier_id': 0,
        'order_id': 100,
        'complete_time':"2021-01-10T10:33:01.42Z"
    }
    test('complete not existing order',
         complete_order(0, 100, shift(100)),
         (400, 'Bad Request'))
    
    test('complete order 12', complete_order(0, 12, shift(15)), (200, 'OK'))
    test('complete order 14', complete_order(0, 14, shift(25)), (200, 'OK'))
    test('complete order 16', complete_order(0, 16, shift(45)), (200, 'OK'))

    json = {'data':[create_order(*dat) for dat in additional_orders]}
    test('post additional orders', post_orders(json), (201, 'Created'))

    test('courier 0 stats', get_courier(0), (200, 'OK'))
    test('courier 1 stats', get_courier(1), (200, 'OK'))

    test('assign orders id=0', assign_orders(0), (200, 'OK'))

    json={
        'courier_id': 0,
        'order_id': 11,
        'complete_time':"2021-01-10T10:33:01.42Z"
    }
    test('complete order 11', complete_order(0, 11, shift(15)), (200, 'OK'))
    json['order_id'] = 21
    test('complete order 21', complete_order(0, 21, shift(17)), (200, 'OK'))

    test('courier 0 stats', get_courier(0), (200, 'OK'))
