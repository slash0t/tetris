class BlockGeometry:
    def __init__(self, coords):
        self.coords = coords

        left = coords[0][0]
        right = left
        up = coords[0][1]
        down = up

        for x, y in coords:
            left = min(left, x)
            right = max(right, x)

            up = max(up, y)
            down = min(down, y)

        self.size = max(right - left, up - down)

    def rotate(self, right):
        new_coords = []

        for coord in self.coords:
            if right:
                now = (coord[1], self.size - coord[0] - 1)
            else:
                now = (self.size - coord[1] - 1, coord[0])
            new_coords.append(now)

        self.coords = new_coords
