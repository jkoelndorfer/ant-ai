from gameboard import Coordinate


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
