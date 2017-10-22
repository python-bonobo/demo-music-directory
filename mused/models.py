from datetime import datetime

from django.db import models
from django.utils.text import slugify


class BaseModel(models.Model):
    created = models.DateTimeField(default=datetime.now, editable=False)
    updated = models.DateTimeField(default=datetime.now, editable=False)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.updated = datetime.now()
        super(BaseModel, self).save(*args, **kwargs)


class RDF(models.Model):
    subject = models.CharField(max_length=255, unique=True, null=False)

    title = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.TextField()

    class Meta:
        abstract = True

    def __str__(self):
        return f'<{type(self).__name__} {self.title}>'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[0:50]
        super(RDF, self).save(*args, **kwargs)


class MusicGenre(RDF, BaseModel):
    pass


class MusicGroup(RDF, BaseModel):
    pass
