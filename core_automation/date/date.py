from __future__ import print_function

from datetime import datetime
from os import makedirs, path


def human_readable_day(day_date):
    date_object = datetime.strptime(day_date, "%Y-%m-%d")
    day_of_week = date_object.strftime("%d-%A")
    return day_of_week


def human_readable_month(month_nb):
    date_object = datetime.strptime(month_nb, "%m")
    return date_object.strftime("%B")


def date_to_folders_tree(save_dir, date, ext="md"):
    only_day_date = date.split(" ")[0]
    save_dir = path.expanduser(save_dir)
    year, month = only_day_date.split("-")[0], only_day_date.split("-")[1]
    human_r_day = human_readable_day(only_day_date)
    human_r_month = human_readable_month(month)
    final_dir = f"{save_dir}/{year}/{human_r_month}"

    if not path.exists(final_dir):
        makedirs(final_dir)

    return f"{final_dir}/{human_r_day}.{ext}"
