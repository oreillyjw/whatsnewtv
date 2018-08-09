from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def setup_paging_controls(data, page=1, num_per_page=20):
    """
        Sets up paging controls for all records
        Found this nice tutorial regarding paging controls
        https://simpleisbetterthancomplex.com/tutorial/2016/08/03/how-to-paginate-with-django.html
    """
    paginator = Paginator(data, num_per_page)

    try:
        data = paginator.page(page)
    except PageNotAnInteger:
        data = paginator.page(1)
    except EmptyPage:
        data = paginator.page(paginator.num_pages)

    return data
