from django.core.management.base import BaseCommand
import deep_engine_client.sysConfig as sysConfig


class StartCommand(BaseCommand):
    help = "please specify the runtime environment. choices: [prod, test]"

    def add_arguments(self, parser):
        # positional args: env
        parser.add_argument('env', type=str, required=True, choices=['prod', 'test'])
        parser.add_argument('--debug', type=bool,
                            des='debug',
                            action='store_true',
                            help="if it will open the debug in settings ")

    def handle(self, *args, **options):
        sysConfig.RUNTIME_ENV = options['env']
        if options['debug']:
            sysConfig.SYS_DEBUG = options['debug']

