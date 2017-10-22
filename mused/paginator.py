import itertools

from django.core.paginator import Paginator as BasePaginator


class Paginator(BasePaginator):
    def page_range(self, first_page, current_page, last_page):
        width = 6 - 1
        start = max(1, current_page - (width // 2))
        end = min(start + width, last_page)
        if (end - start) < width:
            start = max(end - width, first_page)

        if start >= 2:
            prefix = (1, ) if start == 2 else (1, '...')
        else:
            prefix = ()

        if end < last_page:
            return itertools.chain(
                prefix, range(start, end + 1), (last_page, ) if end + 1 == last_page else (
                    '...',
                    last_page,
                )
            )
        else:
            return itertools.chain(prefix, range(start, end + 1))
