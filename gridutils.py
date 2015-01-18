def get_straight_line_coordinates(start, end):
    assert isinstance(start, Coordinate)
    assert isinstance(end, Coordinate)
    assert (start.x == end.x or start.y == end.y)

    if start.x == end.x:
        constant_axis = 'x'
        change_axis = 'y'
    else:
        constant_axis = 'y'
        change_axis = 'x'

    change_coords = (getattr(start, change_axis), getattr(end, change_axis))
    constant_coord = getattr(start, constant_axis)
    min_change_coord = min(change_coords)
    max_change_coord = max(change_coords)

    def generator():
        for i in range(min_change_coord, max_change_coord + 1):
            args = {
                constant_axis: constant_coord,
                change_axis: i
            }
            yield Coordinate(**args)

    return generator()

class Coordinate(object):
    def __init__(self, x, y):
        assert isinstance(x, int)
        assert isinstance(y, int)
        super().__setattr__('x', x)
        super().__setattr__('y', y)

    def __hash__(self):
        return int(str(self.x) + str(self.y))

    def __eq__(self, other):
        return (self.x == other.x and self.y == other.y)

    def __repr__(self):
        return '({0}, {1})'.format(self.x, self.y)

    def __delattr__(self, name):
        raise TypeError('Instances are immutable.')

    def __setattr__(self, name, value):
        raise TypeError('Instances are immutable.')
