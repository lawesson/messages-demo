from django.db import models
from django.db.models import CASCADE

from common.models import TimestampedModel


class User(TimestampedModel):
    """
    A user of messages that keeps track of last read message ID.
    """
    name = models.CharField(max_length=100, primary_key=True,
                            help_text='The identifying name of a receiver of messages')
    last_read_message_id = models.IntegerField(null=True, default=None,
                                               help_text='The message ID of the last read message')
    is_supervisor = models.BooleanField(default=False, help_text='A supervisor iterates over all messages of the '
                                                                 'system, not only her own messages.')


class Message(TimestampedModel):
    class Meta:
        ordering = ['id']

    user = models.ForeignKey(User, on_delete=CASCADE, help_text='The recipient of the message')
    payload = models.TextField(help_text='The payload, the text, of the message')
