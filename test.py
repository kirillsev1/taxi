from datetime import datetime, timedelta
from time import sleep


class Human:
    def __init__(self, name):
        self.name = name

    def __str__(self) -> str:
        return f'{self.__class__.__name__} {self.name}'


class Event:
    def __init__(self, title: str, city: str, human: Human, start: datetime = None, end: datetime = None) -> None:
        self.city = city
        self.title = title
        self.human = human
        self._start = start
        self._end = end

    def start(self) -> None:
        if self._start:
            if self._start <= datetime.now():
                print(f'{self.title} is already started')
                return
            print(f'{self.title} is starting before scheduled date: {self._start}')
        self._start = datetime.now()

    def end(self) -> None:
        if self._end:
            if self._end <= datetime.now():
                print(f'{self.title} is already ended')
                return
            print(f'{self.title} is ended before scheduled date: {self._end}')
        self._end = datetime.now()

    def is_alive(self) -> bool:
        is_started = self._start and self._start <= datetime.now()
        not_ended = self._end and self._end > datetime.now() or not self._end
        return is_started and not_ended and self._start < self._end

    def is_finished(self) -> bool:
        return self._start and self._end and self._start < self._end < datetime.now()

    def get_duration(self) -> timedelta:
        if self.is_finished():
            return self._end - self._start


class Adapter:

    @staticmethod
    def get_hours(event: Event) -> float:
        duration = event.get_duration()
        if duration:
            return duration.total_seconds() / 3600


class Department:

    def __init__(self, city: str, rate: float) -> None:
        self.city = city
        self.rate = rate

    def pay(self, event: Event):
        hours = Adapter.get_hours(event)
        if hours:
            print(f'{hours * self.rate} are to be paid to {event.human}')
        else:
            print(f'{event.human} didn`t work at that time')


if __name__ == '__main__':
    human = Human('Max2288282828')
    event = Event('Поход в НИИ', 'Сириус', human)
    department = Department('Сириус', 10.10)
    event.start()
    sleep(1)
    event.end()
    department.pay(event)
