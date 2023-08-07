# -*- coding: utf-8 -*-

"""Helpers to fit scalar values into sequences.

SPDX-FileCopyrightText: Uwe Krien <krien@uni-bremen.de>
SPDX-FileCopyrightText: Simon Hilpert
SPDX-FileCopyrightText: Cord Kaldemeyer
SPDX-FileCopyrightText: henhuy

SPDX-License-Identifier: MIT

"""

from collections import UserList
from collections import abc
from itertools import repeat


def sequence(iterable_or_scalar):
    """
    This function checks whether an object is a mutable or immutable
    iterable (excluding strings) or a scalar.
    If the object is a mutable
    iterable, it returns the original sequence. For a scalar or string object,
    it returns an 'emulated' sequence object of the class _Sequence with a
    default value.
    If the object is an immutable iterable, it returns an
    'emulated' sequence object of class _Sequence with periodic values, and
    the total length is determined by the first value of the iterable.


    Parameters
    ----------
    iterable_or_scalar : iterable or None or int or float

    Examples
    --------
    >>> sequence([1,2])
    [1, 2]

    >>> x = sequence(10)
    >>> x[0]
    10

    >>> x[10]
    10
    >>> print(x)
    [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10]

    >>> x = sequence({"len":9,"values":[0,1,2]})
    >>> print(x)
    [0, 0, 0, 1, 1, 1, 2, 2, 2]
    >>> x[1]
    0
    >>> x[4]
    1
    >>> x[7]
    2


    """
    if isinstance(iterable_or_scalar, abc.Iterable) and not isinstance(
        iterable_or_scalar, str
    ):
        if isinstance(iterable_or_scalar, abc.MutableMapping):
            if (
                iterable_or_scalar["len"] % len(iterable_or_scalar["values"])
                != 0
            ):
                raise KeyError(
                    "The length must be a multiple of the number of periodic"
                    " values!"
                )
            return _Sequence(
                highest_index=iterable_or_scalar.get("len"),
                periodic_values=iterable_or_scalar.get("values"),
            )
        else:
            return iterable_or_scalar
    else:
        return _Sequence(default=iterable_or_scalar)


class _Sequence(UserList):
    """Emulates a list whose length is not known in advance if default
    is passed. If periodic_values and highest_index are passed, the length
    is known in advance and the sequence is periodic. The periods will have
    the values passed in periodic_values and the lengths of the periods are
    equal and sum up to the value of highest_index.

    Parameters
    ----------
    source:
    default: int or float or string
        Default value for the sequence
    periodic_values: iterable
        Values for the periods of the sequence
    highest_index: int
        The highest index of the sequence (default: -1)


    Examples
    --------
    >>> s = _Sequence(default=42)
    >>> len(s)
    0
    >>> s[1]
    42
    >>> s[2]
    42
    >>> len(s)
    3
    >>> s
    [42, 42, 42]
    >>> s[8]
    42

    >>> s = _Sequence(periodic_values=[0,1,2], highest_index=9)
    >>> len(s)
    9
    >>> s[1]
    0
    >>> s[4]
    1
    >>> s[7]
    2
    >>> s
    [0, 0, 0, 1, 1, 1, 2, 2, 2]


    """

    def __init__(
        self,
        *args,
        default=None,
        periodic_values=None,
        highest_index=-1,
        **kwargs,
    ):
        if all([default is not None, periodic_values is not None]):
            raise ValueError("Only default or periods must be given.")
        self.default = default
        self.periodic_values = periodic_values
        self.default_changed = False
        self.highest_index = highest_index
        self.period_length = (
            int(highest_index / len(periodic_values))
            if periodic_values
            else None
        )
        super().__init__(*args)

    def _get_period_(self, key):
        period = key // self.period_length
        return period

    def __getitem__(self, key):
        if self.periodic_values:
            period = self._get_period_(key)
            return self.periodic_values[period]
        else:
            self.highest_index = max(self.highest_index, key)
            return self.default

    def __init_list(self):
        if self.periodic_values:
            self.data = [
                value
                for value in self.periodic_values
                for _ in range(self.period_length)
            ]
        else:
            self.data = [self.default] * (self.highest_index + 1)

    def __repr__(self):
        return str([i for i in self])

    def __len__(self):
        if self.periodic_values:
            return self.highest_index
        else:
            return max(len(self.data), self.highest_index + 1)

    def __iter__(self):
        if self.periodic_values:
            return iter(
                [
                    value
                    for value in self.periodic_values
                    for _ in range(self.period_length)
                ]
            )
        else:
            return repeat(self.default, self.highest_index + 1)
