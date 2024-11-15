from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import transaction
import logging
import time

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Load all initial fixtures in the correct order with error handling'

    def handle(self, *args, **options):
        fixtures = [
            {
                'app': 'allergens',
                'fixture': 'initial_allergens',
                'dependencies': []
            },
            {
                'app': 'flavours',
                'fixture': 'initial_flavour_categories',
                'dependencies': []
            },
            {
                'app': 'flavours',
                'fixture': 'initial_flavours',
                'dependencies': ['allergens', 'flavours']
            },
            {
                'app': 'products',
                'fixture': 'initial_product_category.json',
                'dependencies': []
            },
            {
                'app': 'products',
                'fixture': 'initial_products.json',
                'dependencies': ['products']
            }
        ]

        for fixture in fixtures:
            retries = 3
            while retries > 0:
                try:
                    with transaction.atomic():
                        self.stdout.write(
                            self.style.WARNING(
                                f'Loading {fixture["app"]} fixture: {fixture["fixture"]}'
                            )
                        )

                        call_command(
                            'loaddata',
                            fixture["fixture"],
                            verbosity=1
                        )

                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Successfully loaded {fixture["fixture"]}'
                            )
                        )
                    break  # Success, exit retry loop

                except Exception as e:
                    retries -= 1
                    if retries > 0:
                        self.stdout.write(
                            self.style.WARNING(
                                f'Error loading {fixture["fixture"]}, retrying... ({retries} attempts left)'
                            )
                        )
                        self.stdout.write(self.style.ERROR(str(e)))
                        time.sleep(2)  # Wait before retry
                    else:
                        self.stdout.write(
                            self.style.ERROR(
                                f'Failed to load {fixture["fixture"]} after all attempts'
                            )
                        )
                        raise e
