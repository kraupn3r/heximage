from django.core.management.base import BaseCommand, CommandError
from picstore.models import TimedImageLink
from django.utils import timezone


class Command(BaseCommand):
    help = 'removes expired TimedImageLinks from database'

    def handle(self, *args, **options):
        link_count = 0
        for link in TimedImageLink.objects.all():
            if link.expire_by_date < timezone.now():
                link.delete()
                link_count += 1
        self.stdout.write(self.style.SUCCESS(
            'Successfully removed {} expired links'.format(link_count)))
