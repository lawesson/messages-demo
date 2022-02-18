from django.db.models import Manager
from django.db.transaction import atomic
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from broker.models import Message, User


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'


class IdListSerializer(serializers.Serializer):
    ids = serializers.ListSerializer(child=serializers.IntegerField(), help_text='A list of IDs to be deleted', required=False)
    start_id = serializers.IntegerField(help_text='First ID to be deleted', required=False)
    end_id = serializers.IntegerField(help_text='Last ID to be deleted', required=False)


class DeleteResultSerializer(serializers.Serializer):
    delete_count = serializers.IntegerField(help_text='The number of entries deleted')


class MessageViewSet(ModelViewSet):
    """
    retrieve:
    Retrieve a message by ID.

    list:
    Retrieve a list of messages. Allowed query parameters are `page` (to supply a page number) and `page_size`.

    create:
    Create a new message.

    partial_update:
    Update some aspect of an existing message.

    destroy:
    Delete a message by ID.
    """
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    @swagger_auto_schema(request_body=IdListSerializer(), responses={200: DeleteResultSerializer(),
                                                                     204: DeleteResultSerializer()})
    @action(methods=['post'], detail=False)
    def bulk_delete(self, request):
        """
        Delete a set of messages.
        """
        incoming = IdListSerializer(data=request.data)
        incoming.is_valid(raise_exception=True)
        body = incoming.validated_data
        ids = body['ids']
        start_id, end_id = body['start_id'], body['end_id']
        if ids is None and start_id is None and end_id is None:
            # We could of course allow the user to shoot themselves in the foot, but this is a reasonable sanity check
            raise ValidationError('Either supply ids or start_id or end_id.')
        messages = Message.objects
        if ids:
            messages = messages.filter(id__in=ids)
        if start_id is not None:
            messages = messages.filter(id__gte=start_id)
        if end_id is not None:
            messages = messages.filter(id__lte=end_id)
        deleted, _row_count = messages.delete()
        return Response(DeleteResultSerializer(dict(delete_count=deleted)).data, status=200 if deleted else 204)


class MessageUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class AnonymousMessageSerializer(serializers.Serializer):
    payload = serializers.CharField(help_text='The message text', required=True)


class UserViewSet(ModelViewSet):
    """
     retrieve:
     Retrieve a user by ID.

     list:
     Retrieve a list of users. Allowed query parameters are `page` (to supply a page number) and `page_size`.

     create:
     Create a new user that can be used as recipient of messages.

     partial_update:
     Update some aspect of an existing user.

     destroy:
     Delete a user by ID.
     """

    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    queryset = User.objects.all()
    serializer_class = MessageUserSerializer

    @swagger_auto_schema(responses={200: MessageSerializer(many=True), 404: 'If user is not found'})
    @action(methods=['get'], detail=True)
    def new_messages(self, request, pk):
        """
        Retrieve a list of new messages, i.e., messages not yet seen by the user. Query parameter `page_size` is allowed, but not `page`.
        """
        with atomic():
            manager: Manager = User.objects
            try:
                user: User = manager.select_for_update().filter(name=pk).get()
                last_read = user.last_read_message_id or 0
                if 'page' in request.query_params:
                    # We cannot allow to have "holes" in the seen messages, since we keep track via a single pointer
                    raise ValidationError('You may not select page number when fetching new messages.')
                messages = Message.objects if user.is_supervisor else user.message_set
                new_messages = messages.order_by('id').filter(id__gt=last_read)
                paginated_qs = self.paginate_queryset(new_messages)
                if paginated_qs:
                    user.last_read_message_id = paginated_qs[-1].id
                    user.save()
                return self.get_paginated_response(MessageSerializer(paginated_qs, many=True).data)
            except User.DoesNotExist:
                return Response(status=404)
