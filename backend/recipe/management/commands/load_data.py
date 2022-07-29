"""Команда загрузки в БД данных из файлов формата *.csv."""
import csv

from django.core.management.base import BaseCommand

from recipe.models import Ingredient, Tag


class Command(BaseCommand):
    help = 'Loads ingredients from a csv file'

    def handle(self, *args, **options):
        with open('./data/ingredients.csv', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                name, unit = row
                Ingredient.objects.get_or_create(
                    name=name,
                    measurement_unit=unit
                )
        self.stdout.write(
            self.style.SUCCESS('Successfully loaded ingredients')
        )
        with open('./data/tags.csv', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                name, slug, color = row
                Tag.objects.get_or_create(
                    name=name,
                    slug=slug,
                    color=color
                )
        self.stdout.write(
            self.style.SUCCESS('Successfully loaded tags')
        )
