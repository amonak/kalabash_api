"""Kalabash API models."""

from dateutil.relativedelta import relativedelta

from django.db import models
from django.utils import timezone


class KalabashInstanceManager(models.Manager):
    """Custom manager for KalabashInstance."""

    def active(self):
        """Return active instances (last_request <= 1 month)."""
        return self.get_queryset().filter(
            last_request__gte=timezone.now() - relativedelta(months=1))


class KalabashInstance(models.Model):
    """A model to represent a kalabash instance."""

    hostname = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField()
    known_version = models.CharField(max_length=30)
    created = models.DateTimeField(auto_now_add=True)
    last_request = models.DateTimeField(auto_now=True)

    # Statistics
    domain_counter = models.PositiveIntegerField(default=0)
    domain_alias_counter = models.PositiveIntegerField(default=0)
    mailbox_counter = models.PositiveIntegerField(default=0)
    alias_counter = models.PositiveIntegerField(default=0)

    # Used extensions
    extensions = models.ManyToManyField("KalabashExtension", blank=True)

    objects = KalabashInstanceManager()

    def __str__(self):
        return "[{0}] {1} -> {2}".format(
            self.ip_address, self.hostname, self.known_version)


class KalabashExtension(models.Model):
    """A kalabash extension with its latest version."""

    name = models.CharField(max_length=255, unique=True)
    version = models.CharField(max_length=30)

    def __str__(self):
        return self.name
