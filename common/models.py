from django.db import models


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, help_text='The creation date of this entity')
    updated_at = models.DateTimeField(auto_now=True, help_text='The last date this entity was updated')

    class Meta:
        abstract = True
        ordering = ['-created_at', '-updated_at']
