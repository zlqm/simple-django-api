import django


def django_after_2_2():
    """check whether django version greater than 2.2
    """
    return django.__version__[:3] > '2.2'
