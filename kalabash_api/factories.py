"""API factories."""

import factory

from . import models


class KalabashExtensionFactory(factory.DjangoModelFactory):
    """Factory for KalabashExtension."""

    class Meta:
        model = models.KalabashExtension

    version = "1.0.0"


class KalabashInstanceFactory(factory.DjangoModelFactory):
    """Factory for KalabashInstance."""

    class Meta:
        model = models.KalabashInstance

    ip_address = "1.2.3.4"
    known_version = "1.0.0"
