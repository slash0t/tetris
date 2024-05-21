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

        self.width = right - left
        self.height = up - down

