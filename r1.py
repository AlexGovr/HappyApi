
from couriers.models import opt_byweight as opt
from couriers.models import Order
ww = [10, 8, 3, 3, 2, 2, 1]
orders = [Order(delivery_hours='', region='', weight=w) for w in ww]
print(opt(orders, 20))