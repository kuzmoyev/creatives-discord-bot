from django.core.management.base import BaseCommand

from bot.bot import bot


class Command(BaseCommand):
    help = 'Run the bot'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting bot...'))
        bot.run()
