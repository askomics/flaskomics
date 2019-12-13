import random
import re
import time
import traceback
import sys


class Utils():
    """Contain utils fonction and classes"""

    @staticmethod
    def redo_if_failure(logger, max_redo, sleep_time, call, *args):
        """Redo a function if it fail, with a sleep time between each try

        Parameters
        ----------
        logger : app.logger
            The flask logger to log error
        max_redo : int
            Max number of try
        sleep_time : int
            Time between each try.
        call : function
            The function to redo if faliure
        *args
            Args of the function
        """
        i = 0
        while True:
            i += 1
            try:
                call(*args)
                break
            except Exception as e:
                if i == max_redo:
                    raise(e)
                traceback.print_exc(file=sys.stdout)
                logger.debug("Fail to execute {}. Retrying in {} sec...".format(call.__name__, sleep_time))
                time.sleep(sleep_time)
                sleep_time = sleep_time * 2
                continue  # redo

    @staticmethod
    def is_valid_url(url):
        """Test if a string an url

        Parameters
        ----------
        url : string
            The url to test

        Returns
        -------
        bool
            True is url is valid
        """
        regex = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$',
            re.IGNORECASE)

        return re.match(regex, url) is not None

    @staticmethod
    def get_random_string(number):
        """return a random string of n character

        Parameters
        ----------
        number : int
            number of character of the random string

        Returns
        -------
        str
            a random string of n chars
        """
        alpabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
        return ''.join(random.choice(alpabet) for i in range(number))

    @staticmethod
    def camel_case(string):
        """camelCase a string"""
        return ''.join(x for x in string.title() if not x.isspace())

    @staticmethod
    def unique(l):
        """return the list with duplicate elements removed and keep order"""
        return [i for n, i in enumerate(l) if i not in l[n + 1:]]

    @staticmethod
    def intersect(a, b):
        """return the intersection of two lists"""
        return list(set(a) & set(b))

    @staticmethod
    def union(a, b):
        """return the union of two lists"""
        return list(set(a) | set(b))

    @staticmethod
    def humansize_to_bytes(hsize):
        """Convert human-readable string into bytes

        Parameters
        ----------
        hsize : string
            Human readable string

        Returns
        -------
        int
            Bytes
        """
        units = {
            "b": 1,
            "kb": 10**3,
            "mb": 10**6,
            "gb": 10**9,
            "tb": 10**12,
            "o": 1,
            "ko": 10**3,
            "mo": 10**6,
            "go": 10**9,
            "to": 10**12,
            "": 1,
            "k": 10**3,
            "m": 10**6,
            "g": 10**9,
            "t": 10**12
        }

        number = ""
        unit = ""
        for char in ''.join(hsize.lower().split()):

            if char.isdigit() or char == ".":
                number += char
            else:
                unit += char.lower()
        number = float(number)

        if number == 0:
            return 0
        return int(number * units[unit])

    @staticmethod
    def is_url(url):
        """Check is string is an url

        Parameters
        ----------
        url : string
            string to test

        Returns
        -------
        bool
            True if string is url
        """
        regex = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$',
            re.IGNORECASE)
        return re.match(regex, url) is not None


class cached_property(object):
    """Like @property on a member function, but also cache the calculation in
    self.__dict__[function name].
    The function is called only once since the cache stored as an instance
    attribute override the property residing in the class attributes. Following accesses
    cost no more than standard Python attribute access.
    If the instance attribute is deleted the next access will re-evaluate the function.
    Source: https://blog.ionelmc.ro/2014/11/04/an-interesting-python-descriptor-quirk/

    usage
    -----
    class Shape(object):

        @cached_property
        def area(self):
            # compute value
            return value

    Attributes
    ----------
    func : TYPE
        Description
    """
    __slots__ = ('func')

    def __init__(self, func):

        self.func = func

    def __get__(self, obj, cls):

        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value
