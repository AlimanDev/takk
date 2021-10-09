from rest_framework import pagination
from rest_framework.response import Response


class MobilePagination(pagination.PageNumberPagination):
    page_size = 15
    page_size_query_param = 'page_size'
    max_page_size = 10000

    def get_paginated_response(self, data):
        return Response({

            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'page': self.page.number,
            'results': data
        })


class DashboardPagination(pagination.PageNumberPagination):
    page_size_query_param = 'limit'
    page_size = 1000

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'page': self.page.number,
            'total_objects': self.page.paginator.count,
            'current_page_size': len(self.page.object_list),
            'limit': self.page.paginator.per_page,
            'total_pages': self.page.paginator.num_pages,
            'results': data
        })

