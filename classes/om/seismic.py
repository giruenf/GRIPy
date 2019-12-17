from classes.om import Density


class Seismic(Density):
    tid = 'seismic'
    _TID_FRIENDLY_NAME = 'Seismic'

    _SHOWN_ATTRIBUTES = [
        ('_oid', 'Object Id')
    ]

    def __init__(self, data, **attributes):
        super().__init__(data, **attributes)

    def _get_max_dimensions(self):
        return 5
