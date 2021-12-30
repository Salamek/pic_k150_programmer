class hex_int(int):
    # @TODO WTH?
    """Behaves just like an integer, except its __repr__ in python yields a hex string."""

    def __init__(self, value, radix=16):
        int.__init__(self, value, radix)

    def __repr__(self):
        if self >= 0:
            return hex(self)
        else:
            # Avoid "future" warning and ensure eval(repr(self)) == self
            return '-' + hex(-self)

    def maybe_hex_int(value):
        if isinstance(value, int):
            return hex_int(value)
        else:
            return value

    maybe_hex_int = staticmethod(maybe_hex_int)

    _method_wrap = lambda super_method_name: lambda *args, **argd: hex_int.maybe_hex_int(int.__dict__[super_method_name](*args, **argd))

    __abs__ = _method_wrap('__abs__')
    __add__ = _method_wrap('__add__')
    __and__ = _method_wrap('__and__')
    __floordiv__ = _method_wrap('__floordiv__')
    __invert__ = _method_wrap('__invert__')
    __lshift__ = _method_wrap('__lshift__')
    __mod__ = _method_wrap('__mod__')
    __mul__ = _method_wrap('__mul__')
    __neg__ = _method_wrap('__neg__')
    __or__ = _method_wrap('__or__')
    __pos__ = _method_wrap('__pos__')
    __pow__ = _method_wrap('__pow__')
    __sub__ = _method_wrap('__sub__')
    __xor__ = _method_wrap('__xor__')
    __radd__ = _method_wrap('__add__')
    __rand__ = _method_wrap('__and__')
    __rfloordiv__ = _method_wrap('__floordiv__')
    __rmul__ = _method_wrap('__mul__')
    __ror__ = _method_wrap('__or__')
    __rsub__ = _method_wrap('__rsub__')
    __rxor__ = _method_wrap('__xor__')


def indexwise_and(fuses, setting_values):
    """Given a list of fuse values, and a list of (index, value) pairs,
    return a list x such that x[index] = fuses[index] & value."""

    result = [x for x in fuses]
    for (index, value) in setting_values:
        result[index] = result[index] & value
    return result


def swab_record(record):
    """Given a record from a hex file, return a new copy with adjacent data bytes swapped."""
    result = []

    for x in range(0, len(record[1]), 2):
        result += record[1][x + 1]
        result += record[1][x]

    return record[0], ''.join(result)


def range_filter_records(records, lower_bound, upper_bound):
    """Given a list of HEX file records, return a new list of HEX file records containing only the HEX data within the specified address range."""
    result = []

    for record in records:
        # Need to handle five cases:
        # 1: record is completely below lower bound - do nothing
        # 2: record is partially below lower bound - slice and append
        # 3: record is in range - append
        # 4: record is partially above upper bound - slice and append
        # 5: record is completely above upper bound - do nothing
        if ((record[0] >= lower_bound) and
                (record[0] < upper_bound)):
            # lower bound is in range and therefore needn't change.
            # Part or all of this record will appear in output.
            if (record[0] + len(record[1])) < upper_bound:
                # case 3
                result.append(record)
            else:
                # case 4
                slice_length = upper_bound - record[0]
                result.append((record[0], record[1][0:slice_length]))
        elif ((record[0] < lower_bound) and
              ((record[0] + len(record[1])) > lower_bound)):
            # case 2
            slice_pos = (lower_bound - record[0])
            result.append((lower_bound, record[1][slice_pos:len(record[1])]))
    return result


def merge_records(records, default_data, base_address=0):
    """Given a list of HEX file records and a data buffer with its own base address (default=0), merge the HEX file records into a new copy of the data buffer."""
    result_list = []

    mark = 0
    for record in records:
        if ((record[0] < base_address) or
                ((record[0] + len(record[1])) > (base_address +
                                                 len(default_data)))):
            raise IndexError('Record out of range.')

        point = (record[0] - base_address)
        if mark != point:
            result_list += default_data[mark:point]
            mark = point
        # Now we can add the record data to result_list.
        result_list += record[1]
        mark += len(record[1])
    # Fill out the rest of the result with data from default_data, if
    # necessary.
    if mark < len(default_data):
        result_list += default_data[mark:]

    # String-join result_list and return.
    return ''.join(result_list)
