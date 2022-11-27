from axes.backends import AxesBackend
from django.contrib.auth.backends import ModelBackend

class AxesBackend(AxesBackend, ModelBackend):
    pass
