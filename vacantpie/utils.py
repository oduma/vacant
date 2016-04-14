def format_date(day):
    d_year = day.year
    d_month = day.month
    d_day = day.day
    return str(d_year) + "-" + str(d_month).zfill(2) + "-" + str(d_day).zfill(2)
