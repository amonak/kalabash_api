"""Dashboard views."""

from collections import OrderedDict
import datetime

from dateutil.relativedelta import relativedelta

from django.db.models import Count, Sum
from django.utils import timezone
from django.views import generic

from django.contrib.auth import mixins as auth_mixins

from kalabash_api import models

from . import tools

MONTH_FORMAT = "%m%Y"


class DashboardView(auth_mixins.LoginRequiredMixin, generic.TemplateView):
    """Dashboard view."""

    template_name = "dashboard/base.html"

    def get_context_data(self, **kwargs):
        """Add data to context."""
        context = super(DashboardView, self).get_context_data(**kwargs)
        instances_per_version = OrderedDict()
        now = timezone.now()
        month = datetime.datetime.strptime(
            self.request.GET.get("month", now.strftime(MONTH_FORMAT)),
            MONTH_FORMAT)
        all_qset = models.KalabashInstance.objects.all().order_by(
            "known_version")
        # Only consider the last month
        analyzed_period = now - relativedelta(months=1)
        for instance in all_qset.filter(last_request__gte=analyzed_period):
            key = str(instance.known_version)
            if key not in instances_per_version:
                instances_per_version[key] = 0
            instances_per_version[key] += 1
        instances_per_version = [
            [str(version), counter]
            for version, counter in instances_per_version.items()]

        temp_dict = {}
        tz = timezone.get_current_timezone()
        from_datetime = tz.localize(month)
        end_date = min(
            (from_datetime + relativedelta(months=1, days=-1)).date(),
            now.date())
        qset = models.KalabashInstance.objects.filter(
            created__gte=from_datetime, created__date__lte=end_date)
        for instance in qset:
            date = instance.created.date()
            if date not in temp_dict:
                temp_dict[date] = 0
            temp_dict[date] += 1
        new_instances_per_day = OrderedDict()
        cur_date = from_datetime.date()
        while cur_date <= end_date:
            new_instances_per_day[cur_date.isoformat()] = (
                temp_dict.get(cur_date, 0))
            cur_date += relativedelta(days=1)
        prev_month = (month - relativedelta(months=1)).strftime("%m%Y")
        next_month = (month + relativedelta(months=1)).strftime("%m%Y")
        counters = models.KalabashInstance.objects.all().aggregate(
            total=Count("pk"),
            domain_counter=Sum("domain_counter"),
            mailbox_counter=Sum("mailbox_counter"),
            alias_counter=Sum("alias_counter"),
        )

        extension_counters = []
        extensions = models.KalabashExtension.objects.all().annotate(
            total=Count("kalabashinstance"))
        for extension in extensions:
            extension_counters.append([str(extension.name), extension.total])

        services, period = tools.parse_access_logs()
        hits_by_service = []
        ips_by_service = []
        total_hits = 0
        for service, stats in services.items():
            total_hits += stats["total"]
            hits_by_service.append([service, stats["total"]])
            ips_by_service.append([service, len(stats["ips"])])
        hits_by_second = total_hits / ((period[1] - period[0]).total_seconds())
        nb_days = (end_date - from_datetime.date()).days or 1
        context.update({
            "month": month.strftime("%b %Y"),
            "prev_month": prev_month,
            "next_month": next_month,
            "counters": counters,
            "active_instances": all_qset.filter(
                last_request__gte=analyzed_period).count(),
            "instances_sending_stats": all_qset.filter(
                last_request__gte=analyzed_period, known_version__gte="1.6.0")
            .count(),
            "new_instances_this_month": qset.count(),
            "average_instance_per_day": qset.count() / nb_days,
            "instances_per_version": instances_per_version,
            "new_instances_per_day": new_instances_per_day,
            "extension_counters": extension_counters,
            "hits_by_service": hits_by_service,
            "ips_by_service": ips_by_service,
            "hits_by_second": hits_by_second,
            "logs_period": period
        })
        return context
