# coding: utf-8

"""
    django forms addons
    ~~~~~~~~~~~~~~~~~~~



    :copyleft: 2008-2011 by the PyRM team, see AUTHORS for more details.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

from __future__ import division, absolute_import
import os
import copy
import datetime
import calendar

from django import forms

ROMAN_QUARTER_DATA = {
    "I"  : (1, 3),
    "II" : (4, 6),
    "III": (7, 9),
    "IV" : (10, 12),
}
ROMAN_NUMERALS = ROMAN_QUARTER_DATA.keys() # ['I', 'II', 'III', 'IV']


class QuarterChoiceField(forms.ChoiceField):
    """
    >>> start = datetime.date(2007, 1, 1)
    >>> end = datetime.date(2008, 12, 31)
    
    
    >>> t = QuarterChoiceField(epoch = (start, end), reverse=True)
    >>> t.choices
    [(0, 'IV.2008'), (1, 'III.2008'), (2, 'II.2008'), (3, 'I.2008'), \
(4, 'IV.2007'), (5, 'III.2007'), (6, 'II.2007'), (7, 'I.2007')]
    >>> t.clean(0)
    (datetime.date(2008, 10, 1), datetime.date(2008, 12, 31))
    >>> t.clean(7)
    (datetime.date(2007, 1, 1), datetime.date(2007, 3, 31))
    
    
    >>> t = QuarterChoiceField(epoch = (start, end))
    >>> t.choices
    [(0, 'I.2007'), (1, 'II.2007'), (2, 'III.2007'), (3, 'IV.2007'), \
(4, 'I.2008'), (5, 'II.2008'), (6, 'III.2008'), (7, 'IV.2008')]
    >>> t.clean(2)
    (datetime.date(2007, 7, 1), datetime.date(2007, 9, 30))

    >>> print "1"
    >>> t = QuarterChoiceField(epoch = (None, None), reverse=True)
    >>> t.choices
    
    
    >>> t = QuarterChoiceField(epoch = (start, start))
    >>> t.choices


    >>> t = QuarterChoiceField(epoch = (end, start))
    >>> t.choices    
    """
    def __init__(self, *args, **kwargs):
        """
        kwarg 'epoch' must be two datetime objects.
        """
        epoch = kwargs.pop("epoch")
        self.oldest = min(epoch)
        self.newest = max(epoch)

#        self.oldest, self.newest = kwargs.pop("epoch")
        if self.oldest == None and self.newest == None:
            self.newest = datetime.datetime.now()
            delta = datetime.timedelta(days=365)
            self.oldest = self.newest - delta


        assert(self.oldest <= self.newest), "Wrong: %r < %r" % (self.oldest, self.newest)

        self.reverse = kwargs.pop("reverse", False)
        super(QuarterChoiceField, self).__init__(*args, **kwargs)

        self.time_range = range(self.oldest.year, self.newest.year)

        self.roman_range = copy.copy(ROMAN_NUMERALS)
        if self.reverse:
            self.time_range.reverse()
            self.roman_range.reverse()

        self.choices = self._build_choices()

    def clean(self, value):
        """
        FIXME: Find a better solution!
        """
        value = super(QuarterChoiceField, self).clean(value)
        index = int(value)

        string_repr = self.choices[index][1]
        quarter, year = string_repr.split(".")
        year = int(year)

        start_month, end_month = ROMAN_QUARTER_DATA[quarter]

        start = datetime.date(year, start_month, 1)

        day_count = calendar.monthrange(year, end_month)[1]
        end = datetime.date(year, end_month, day_count)

        return start, end

    def _build_choices(self):
        """
        FIXME: Nur die wirklichen Quartale sollten genommen werden und nicht
            alle des Jahres.        
        """
        choices = []
        no = 0
        for year in self.time_range:
            for roman in self.roman_range:
                choices.append(
                    (no, "%s.%s" % (roman, year))
                )
                no += 1
        return choices


class ExtFileField(forms.FileField):
    """
    Same as forms.FileField, but you can specify a file extension whitelist.
    
    >>> from django.core.files.uploadedfile import SimpleUploadedFile
    >>>
    >>> t = ExtFileField(ext_whitelist=(".pdf", ".txt"))
    >>>
    >>> t.clean(SimpleUploadedFile('filename.pdf', 'Some File Content'))
    >>> t.clean(SimpleUploadedFile('filename.txt', 'Some File Content'))
    >>>
    >>> t.clean(SimpleUploadedFile('filename.exe', 'Some File Content'))
    Traceback (most recent call last):
    ...
    ValidationError: [u'Not allowed filetype!']
    """
    def __init__(self, *args, **kwargs):
        ext_whitelist = kwargs.pop("ext_whitelist")
        self.ext_whitelist = [i.lower() for i in ext_whitelist]

        super(ExtFileField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        data = super(ExtFileField, self).clean(*args, **kwargs)
        filename = data.name
        ext = os.path.splitext(filename)[1]
        ext = ext.lower()
        if ext not in self.ext_whitelist:
            raise forms.ValidationError("Not allowed filetype!")

if __name__ == "__main__":
    import doctest, datetime
    doctest.testmod(
#        verbose=True
        verbose=False
    )
    print "DocTest end."
