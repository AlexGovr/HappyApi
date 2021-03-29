import datetime
from time import strptime, strftime

_offset = datetime.timedelta(hours=0)
tz = datetime.timezone(_offset)


def parse_timeint(timeinterval):
    stamps = timeinterval.split('-')
    begin = parse_time(stamps[0])
    end = parse_time(stamps[1])
    return begin, end


def parse_time(time_str):
    return strptime(time_str, '%H:%M')


def srl_timeint(begin, end):
    return f'{srl_time(begin)}-{srl_time(end)}'


def srl_time(tstring):
    return strftime('%H:%M', tstring)


def datetime_now():
    return datetime.datetime.now(tz).isoformat()


def parse_datetime(dtstring):
    return datetime.datetime.strptime(dtstring, '%Y-%m-%dT%H:%M:%S.%f%z')
