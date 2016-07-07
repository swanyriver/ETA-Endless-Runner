#todo hitbox
#todo colored drawing
#todo don't draw outside of hitbox
#todo animated assets

#todo read from file
#todo visualization program


class drawable():
    def __init__(self, drawing, name):
        assert type(drawing) == list
        assert len(drawing) > 0

        self.height = len(drawing)
        self.width = len(drawing[0])
        assert all(len(row) == self.width for row in drawing)
        self.drawing = drawing
        self.name = name