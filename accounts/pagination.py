from rest_framework import pagination
from rest_framework import serializers

from datetime import datetime
from dateutil.relativedelta import relativedelta


class CustomPagination(pagination.LimitOffsetPagination):
    """
    Custom Limit Offset Paginator for `User`s. \n Requires client to provide `limit` and `offset` parameters.
    """

    default_limit = 100
    max_limit = 1000000
    min_limit = 1
    min_offset = 0
    max_offset = 1000000

    def paginate_queryset(self, queryset, request, view=None):

        limit = request.query_params.get('limit')
        offset = request.query_params.get('offset')

        gender = request.query_params.get('gender')
        min_age = request.query_params.get('min-age')
        max_age = request.query_params.get('max-age')

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

        if gender:

            gender = gender.strip().lower()

            queryset = queryset.filter(gender=gender)

        if min_age and min_age.strip().isnumeric():

            min_age = int(min_age.strip())

            date = datetime.now() - relativedelta(years=min_age)

            queryset = queryset.filter(date_of_birth__year__lte=date.year)

        if max_age and max_age.strip().isnumeric():

            max_age = int(max_age.strip())

            date = datetime.now() - relativedelta(years=max_age)

            queryset = queryset.filter(date_of_birth__year__gte=date.year)

        return super(self.__class__,
                     self).paginate_queryset(queryset, request, view)
