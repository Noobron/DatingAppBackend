from rest_framework import pagination
from rest_framework import serializers


class ChatMessagePagination(pagination.LimitOffsetPagination):
    """
    Custom Limit Offset Paginator for `ChatMessages`s. \n Requires client to provide `limit` and `offset` parameters.
    """

    default_limit = 100
    max_limit = 1000000
    min_limit = 1
    min_offset = 0
    max_offset = 1000000

    def paginate_queryset(self, queryset, request, view=None):

        limit = request.query_params.get('limit')
        offset = request.query_params.get('offset')

        if limit and limit.strip().isnumeric():

            limit = int(limit.strip())

            if limit > self.max_limit:
                raise serializers.ValidationError({
                    "limit": [
                        "Limit should be less than or equal to {0}".format(
                            self.max_limit)
                    ]
                })

            elif limit < self.min_limit:
                raise serializers.ValidationError({
                    "limit": [
                        "Limit should be greater than or equal to {0}".format(
                            self.min_limit)
                    ]
                })

        if offset and offset.strip().isnumeric():

            offset = int(offset.strip())

            if offset > self.max_offset:
                raise serializers.ValidationError({
                    "offset": [
                        "Offset should be less than or equal to {0}".format(
                            self.max_offset)
                    ]
                })

            elif offset < self.min_offset:
                raise serializers.ValidationError({
                    "offset": [
                        "Offset should be greater than or equal to {0}".format(
                            self.min_offset)
                    ]
                })

        count = queryset.filter(seen=False).count()

        _limit = None

        if limit is not None:
            _limit = limit if type(limit) == int else int(
                limit.strip()) if limit.strip().isnumeric() else None

        if count > 0 and (_limit is None or count > _limit):
            if not request.GET._mutable:
                request.GET._mutable = True
            request.GET['limit'] = str(count)

        return super(self.__class__,
                     self).paginate_queryset(queryset, request, view)