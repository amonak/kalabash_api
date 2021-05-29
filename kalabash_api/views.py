"""API views."""
from django.conf import settings

from rest_framework import decorators, mixins, response, status, viewsets
from rest_framework.views import APIView

from .models import KalabashInstance, KalabashExtension
from .forms import ClientVersionForm

from . import constants
from . import models
from . import serializers


# Legacy API, to deprecate

class CurrentVersionView(APIView):

    """Get current kalabash version."""

    def get(self, request, fmt=None):
        if request.GET.get("client_version") == "1.2.0-rc2":
            # Temp. fix
            request.GET = request.GET.copy()
            request.GET["client_version"] = "1.2.0"
        form = ClientVersionForm(request.GET)
        if not form.is_valid():
            return response.Response(
                {"error": (
                    "Client version and/or site is missing or incorrect")},
                status=status.HTTP_400_BAD_REQUEST
            )
        args = {
            "ip_address": request.META.get("REMOTE_ADDR"),
            "hostname": form.cleaned_data["client_site"]
        }
        if KalabashInstance.objects.filter(**args).exists():
            mdinst = KalabashInstance.objects.get(**args)
        elif KalabashInstance.objects.filter(hostname=args["hostname"]).exists():
            mdinst = KalabashInstance.objects.get(hostname=args["hostname"])
            mdinst.ip_address = args["ip_address"]
        elif KalabashInstance.objects.filter(ip_address=args["ip_address"]).exists():
            mdinst = KalabashInstance.objects.get(ip_address=args["ip_address"])
            if args["hostname"] not in constants.BAD_HOSTNAME_LIST:
                mdinst.hostname = args["hostname"]
        elif args["hostname"] not in constants.BAD_HOSTNAME_LIST:
            mdinst = KalabashInstance(**args)
        else:
            mdinst = None
        if mdinst is not None:
            if mdinst.known_version != form.cleaned_data["client_version"]:
                mdinst.known_version = form.cleaned_data["client_version"]
            mdinst.save()
        data = {"version": settings.KALABASH_CURRENT_VERSION[0],
                "changelog_url": settings.KALABASH_CURRENT_VERSION[1]}
        return response.Response(data)


class ExtensionListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """List all defined extensions."""

    queryset = KalabashExtension.objects.all()
    serializer_class = serializers.KalabashExtensionSerializer


# New API

class InstanceViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin,
                      viewsets.GenericViewSet):
    """Create or update instance."""

    queryset = KalabashInstance.objects.all()
    serializer_class = serializers.InstanceSerializer

    @decorators.list_route(methods=["get"])
    def search(self, request, *args, **kwargs):
        """Search an instance."""
        hostname = request.GET.get("hostname")
        if not hostname:
            return response.Response({
                "error": "No hostname provided."
            }, status=status.HTTP_400_BAD_REQUEST)
        ip_address = request.META.get("REMOTE_ADDR")
        instance = models.KalabashInstance.objects.filter(
            ip_address=ip_address, hostname=hostname).first()
        if not instance:
            return response.Response({
                "error": "Instance not found."
            }, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance)
        return response.Response(serializer.data)


class VersionViewSet(viewsets.ViewSet):
    """List all versions."""

    def list(self, request):
        data = []
        for extension in models.KalabashExtension.objects.all():
            data.append({
                "name": extension.name, "version": extension.version,
                "url": ""})
        data.append({
            "name": "kalabash", "version": settings.KALABASH_CURRENT_VERSION[0],
            "url": settings.KALABASH_CURRENT_VERSION[1]
        })
        serializer = serializers.VersionSerializer(data, many=True)
        return response.Response(serializer.data)
