import os
import sys

from django.core.management.base import BaseCommand, CommandError

from vmmanage.deploy_controller import install_available_problems
from vmmanage.models import Problem, vagr_factory


class Command(BaseCommand):
    help = "Updates the database with changes from the challenge repo."

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            "--install",
            action="store_true",
            help="Automatically install new problems from the repo.",
        )

    def handle(self, *args, **options):
        for problem in Problem.objects.all():

            print(f"Updating {problem.name}/{problem.slug} from {problem.path}")
            if not os.path.isdir(problem.relative_path):
                print(
                    self.style.ERROR(
                        f"Problem path {problem.path} (Problem {problem.name}/{Problem.slug}) doesn't exist."
                        "Skipping."
                    ),
                    file=sys.stderr
                )
                continue

            vagr = vagr_factory(problem.path)

            config = vagr.get_config()

            problem.set_basic_config(config)

            problem.save()

        if options["install"]:
            paths = install_available_problems()
            for path in paths:
                print(f"Launching install job for {path}.")
