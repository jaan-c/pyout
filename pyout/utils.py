from typing import *

import datetime


def countdown(count: datetime.timedelta) -> Iterator[datetime.timedelta]:
    assert count > datetime.timedelta()

    start = datetime.datetime.now()
    while True:
        current = datetime.datetime.now()
        difference = current - start
        if difference < count:
            yield difference
        else:
            break
