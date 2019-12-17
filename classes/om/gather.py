from classes.om import Density


class Gather(Density):
    tid = 'gather'
    _TID_FRIENDLY_NAME = 'Gather'
    _SHOWN_ATTRIBUTES = [('datatype', 'Curve Type'),
                         ('unit', 'Unit'),
                         ('min', 'Min Value'),
                         ('max', 'Max Value')
                         ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _get_max_dimensions(self):
        return 5
