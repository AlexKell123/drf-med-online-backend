from rest_framework.exceptions import ValidationError

from med_consultations.models import Consultation, SpecialWorkTime, WorkTime


class ConsultationValidator:
    def __init__(self):
        self.valid_minutes = [0, 20, 40]

    def check_errors(self, date_time, doctor):
        self.check_input_errors(date_time)
        self.check_schedule_errors(date_time, doctor)


    def check_input_errors(self, date_time):
        self.check_seconds(date_time)
        self.check_minutes(date_time)

    def check_schedule_errors(self, date_time, doctor):
        self.check_existing_consultation(date_time, doctor)
        day = self.get_day(date_time, doctor)
        self.check_work_time(date_time, day)


    @staticmethod
    def check_seconds(date_time):
        if date_time.second != 0 or date_time.microsecond != 0:
            raise ValidationError(f'error: Invalid time {date_time.time()}, seconds and microseconds must be 0')

    def check_minutes(self, date_time):
        if date_time.minute not in self.valid_minutes:
            raise ValidationError(f'error: Invalid time {date_time.time()}, minutes must be in {self.valid_minutes}')

    @staticmethod
    def check_existing_consultation(date_time, doctor):
        if Consultation.objects.filter(doctor=doctor, datetime=date_time):
            raise ValidationError(f'error: Consultation already exist: {date_time}')

    @staticmethod
    def get_day(date_time, doctor):
        day = SpecialWorkTime.objects.filter(doctor=doctor, date=date_time.date())
        if not day:
            day = WorkTime.objects.filter(doctor=doctor, day=date_time.date().weekday())
            if not day:
                raise ValidationError(
                    f'error: There are no consultations with this doctor on this day: {date_time.date()}')
        return day

    @staticmethod
    def check_work_time(date_time, day):
        for i in day:
            if i.start_time <= date_time.time() < i.end_time:
                return
        raise ValidationError(
            f'error: There are no consultations with this doctor at this time: {date_time.time()}')
