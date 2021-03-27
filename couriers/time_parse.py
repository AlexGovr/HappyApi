from time import strptime, strftime

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
