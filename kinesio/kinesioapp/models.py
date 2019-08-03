from django.db import models
from users.models import User
from cryptography.fernet import Fernet
from django.conf import settings


PENDING = 'pending'
FINISHED = 'finished'
CANCELLED = 'cancelled'


class Homework(models.Model):
    from_date = models.DateTimeField()
    to_date = models.DateTimeField()
    periodicity = models.IntegerField()


class HomeworkExercise(models.Model):
    HOMEWORK_SESSION_STATUS_CHOICES = [
        ('P', 'PENDING'),
        ('D', 'DONE'),
        ('C', 'CANCELLED')
    ]

    date = models.DateTimeField()
    number_of_homework_session = models.IntegerField()
    status = models.CharField(max_length=100, choices=HOMEWORK_SESSION_STATUS_CHOICES, default='PENDING')
    homework = models.ForeignKey(Homework, on_delete=models.CASCADE, null=True)


class Exercise(models.Model):
    name = models.CharField(max_length=255)
    homework_exercise = models.ForeignKey(HomeworkExercise, on_delete=models.CASCADE, null=True)


class Video(models.Model):
    name = models.CharField(max_length=255)
    owner = models.OneToOneField(User, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, null=True)


class ClinicalHistoryQuerySet(models.QuerySet):
    def accessible_by(self, user: User) -> models.QuerySet:
        return self.filter(patient__in=user.related_patients)


class ClinicalHistory(models.Model):
    CLINICAL_HISTORY_STATUS_CHOICES = [
        ('P', 'PENDING'),
        ('F', 'FINISHED'),
        ('C', 'CANCELLED')
    ]

    date = models.DateTimeField()
    description = models.CharField(max_length=255)
    status = models.CharField(max_length=100, choices=CLINICAL_HISTORY_STATUS_CHOICES, default='PENDING')
    patient = models.ForeignKey(User, on_delete=models.CASCADE)

    objects = ClinicalHistoryQuerySet.as_manager()

    def can_access(self, user: User) -> bool:
        return self.patient in user.related_patients


class ClinicalSession(models.Model):
    SESSION_STATUS_CHOICES = [
        ('P', 'PENDING'),
        ('F', 'FINISHED'),
        ('C', 'CANCELLED')
    ]
    date = models.DateTimeField()
    status = models.CharField(max_length=100, choices=SESSION_STATUS_CHOICES, default='PENDING')
    homework = models.OneToOneField(Homework, on_delete=models.CASCADE, blank=True, null=True)
    clinical_history = models.ForeignKey(ClinicalHistory, related_name='clinical_sessions', on_delete=models.CASCADE)

    def can_access(self, user: User) -> bool:
        return self.clinical_history.can_access(user)


class ImageQuerySet(models.QuerySet):
    def create(self, content: bytes, **kwargs):
        encrypted_content = Fernet(settings.IMAGE_ENCRYPTION_KEY).encrypt(content)
        return super().create(_content=encrypted_content, **kwargs)


class Image(models.Model):
    _content = models.BinaryField()
    clinical_session = models.ForeignKey(ClinicalSession, on_delete=models.CASCADE, null=True)

    objects = ImageQuerySet.as_manager()

    @property
    def content(self) -> bytes:
        return Fernet(settings.IMAGE_ENCRYPTION_KEY).decrypt(self._content.tobytes())

    def can_access(self, user: User) -> bool:
        return self.clinical_session.anyone_has_access(user)
