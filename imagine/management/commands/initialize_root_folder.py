import uuid
from django.core.management.base import BaseCommand
from imagine.models import Folder

class Command(BaseCommand):
    help = 'Initialize the root folder with a predefined UUID'

    def handle(self, *args, **kwargs):
        root_uuid = uuid.UUID('00000000-0000-0000-0000-000000000000')  # or any specific UUID you want
        root_folder, created = Folder.objects.get_or_create(data_id=root_uuid, defaults={'name': 'root'})
        if created:
            self.stdout.write(self.style.SUCCESS('Root folder created successfully'))
        else:
            self.stdout.write(self.style.SUCCESS('Root folder already exists'))