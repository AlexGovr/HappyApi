
def rating(courier, allorders):
    orders = allorders.filter(courier_id=courier, completed=True)
    region_dict = {}
    for ordr in orders:
        region = ordr.region
        reg_orders = region_dict.get(region, [])
        reg_orders.append(ordr)
        region_dict[region] = reg_orders
    # sort order lists
    _ = [l.sort(key=lambda o: o.dlvtime) for l in region_dict.values()]

    min_avrg_dtime = min([average_time(l) for l in region_dict.values()])
    ratio = min_avrg_dtime / (60 * 60)
    r = (1 - min(ratio, 1)) * 5
    return r


def average_time(orders):
    first = orders[0]
    total_time = seconds(first.dlvtime - first.asgntime)
    for ordr, prev in zip(orders[1:], orders[:-1]):
        dt = seconds(ordr.dlvtime - max(ordr.asgntime, prev.dlvtime))
        total_time += dt
    
    return total_time/len(orders)


def seconds(timedelta):
    return timedelta.total_seconds()