from django.core.management.base import BaseCommand, CommandError
from accounts.models import Plan, ThumbSize
class Command(BaseCommand):
    help = 'Create base plans and thumbnail resolutions'


    def handle(self, *args, **options):
        #foreign key here when file is original
        thumb_original = ThumbSize.objects.create(
            height = 0,
        )
        thumb_200 = ThumbSize.objects.create(
            height = 200,
        )
        thumb_400 = ThumbSize.objects.create(
            height = 400,
        )
        plan_basic = Plan.objects.create(
            title = 'Basic',
        )
        plan_basic.thumb_sizes.add(thumb_200)
        plan_premium = Plan.objects.create(
            title = 'Premium',
            enable_original_image = True,
        )
        plan_premium.thumb_sizes.add(thumb_200)
        plan_premium.thumb_sizes.add(thumb_400)

        plan_enterprise = Plan.objects.create(
            title = 'Enterprise',
            enable_original_image = True,
            enable_expiring_link = True
        )
        plan_enterprise.thumb_sizes.add(thumb_200)
        plan_enterprise.thumb_sizes.add(thumb_400)


        self.stdout.write(self.style.SUCCESS('Successfully created base plans'))
