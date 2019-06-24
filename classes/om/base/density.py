from classes.om import DataObject


class Density(DataObject):
    tid = 'density'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        