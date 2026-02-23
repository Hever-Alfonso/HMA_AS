from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    fullName = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=50, blank=True)

    def login(self):
        pass

    def signUp(self):
        pass

    def logOut(self):
        pass

    def __str__(self):
        return self.fullName or self.username
