from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse
from django_includes.jinja2 import DjangoIncludesExtension

from jinja2 import Environment


def environment(**options):
    env = Environment(**options)

    env.globals.update({
        'static': staticfiles_storage.url,
        'url': reverse,
    })

    env.add_extension(DjangoIncludesExtension)

    return env
