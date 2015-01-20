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

    for i in range(min_change_coord, max_change_coord + 1):
        args = {
            constant_axis: constant_coord,
            change_axis: i
        }
        yield Coordinate(**args)

def get_filled_circle_coordinates(center, radius):
    assert isinstance(center, Coordinate)
    r2 = radius**2

    for x in range(-1 * radius, radius + 1):
        x2 = x**2
        for y in range(-1 * radius, radius + 1):
            y2 = y**2
            print("Checking {}, {}".format(x, y))
            if x2 + y2 <= r2:
                yield Coordinate(x + center.x, y + center.y)
