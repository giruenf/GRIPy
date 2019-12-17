from classes.om import Density


class Spectogram(Density):
    tid = 'spectogram'
    _TID_FRIENDLY_NAME = 'Spectogram'
    _SHOWN_ATTRIBUTES = [('datatype', 'Curve Type'),
                         ('unit', 'Unit'),
                         ('min', 'Min Value'),
                         ('max', 'Max Value')
                         ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _get_max_dimensions(self):
        return 5
