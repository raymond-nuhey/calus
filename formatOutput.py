#!/usr/bin/python3
# pjscicalc: a scientific calculator in python/html/javascript
# Copyright (C) 2021 John D Lamb
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import mpmath


##
# Remove '.0' from end of string
##
def strip_point_zero(string):
    l = len(string)
    if '.0' == string[l - 2:l]:
        return string[0:l - 2]
    else:
        return string


##
# Get longest string representation in A±eB format with at most c chars
##
def shrink_sci(double, c):
    l = c
    sci = mpmath.nstr(double, l, min_fixed=0, max_fixed=0)
    L = len(sci)
    while L > c:
        l -= 1
        if l < 1:
            ## Try stripping zero
            sci = sci.split('e')
            sci = strip_point_zero(sci[0]) + 'e' + sci[1]
            L = len(sci)
            if L <= c:
                return sci
            else:
                return 'Error'
        sci = mpmath.nstr(double, l, min_fixed=0, max_fixed=0)
        L = len(sci)
    return sci


##
# Get longest string representation in #.# format with at most c chars
##
def shrink_dec(double, c):
    l = c
    dec = mpmath.nstr(double, l)
    dec_split = dec.split('e')
    if len(dec_split) > 1:
        return 'Error'
    L = len(dec)
    while L > c:
        ## Try stripping zero
        dec = strip_point_zero(dec)
        if len(dec) <= c:
            return dec
        l -= 1
        dec = mpmath.nstr(double, l)
        dec_split = dec.split('e')
        if len(dec_split) > 1:
            return 'Error'
        L = len(dec)
    return dec


##
# Count significant figures
##
def get_sf(st):
    st = st.split('e')[0]  # ignore exponent if any
    st = strip_point_zero(st)  # ignore trailing '.0' if any
    st = st.split('.')  # remove decimal point
    if len(st) > 1:
        st = st[0] + st[1]
    else:
        st = st[0]
    while len(st) > 0 and '0' == st[0]:  # strip leading zeros
        st = st[1:len(st)]
    return len(st)


##
# Format a nonegative float
# @param double The float
# @param chacters The maximum number of characters
##
def preformat(double, characters):
    if double >= 1:
        result = shrink_dec(double, characters)
        if 'Error' != result:
            return result
        else:  ## try Ae±B notation
            return shrink_sci(double, characters)
    else:  # need to know about significant figures
        dec = shrink_dec(double, characters)
        sci = shrink_sci(double, characters)
        if 'Error' == dec:
            return sci
        elif 'Error' == sci:
            return dec
        else:  # find which has more significant figures
            if get_sf(sci) > get_sf(dec):
                return sci
            else:
                return dec


##
# Format a float
# @param double The float
# @param chacters The maximum number of characters
##
def format(double, characters):
    d_abs = mpmath.fabs(double)
    if d_abs == double:
        sign = 1
    else:
        sign = -1
    result = preformat(d_abs, characters)
    ## May have to replace - sign
    result_split = result.split('-')
    if len(result_split) > 1:
        result = result_split[0] + '&minus;' + result_split[1]
    if -1 == sign:
        result = '&minus;' + result
    return result
