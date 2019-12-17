from collections import OrderedDict

import numpy as np

from classes.ui import UIManager
from classes.ui import RepresentationController
from classes.ui import RepresentationView
from basic.colors import COLOR_CYCLE_NAMES


class PatchesRepresentationController(RepresentationController):
    tid = 'patches_representation_controller'

    def __init__(self, **state):
        super().__init__(**state)


class PatchesRepresentationView(RepresentationView):
    tid = 'patches_representation_view'

    def __init__(self, controller_uid):
        super(PatchesRepresentationView, self).__init__(controller_uid)
        # if self.label:
        #    self.label.set_plot_type('partition')

    # def PostInit(self):
    #    self.draw()

    """ TODO: Esta função precisa ser implementada corretamente """

    def get_data_info(self, event):
        return None

    """ TODO: Precisa adicionar as cores automaticamente para os
        respectivos codigos"""

    def draw(self):
        if self._mplot_objects:
            self.clear()

        UIM = UIManager()
        controller = UIM.get(self._controller_uid)

        toc = self.get_parent_controller()

        xdata = toc.get_filtered_data(dimensions_desired=1)
        if xdata is None:
            return
        #
        ydata = toc.get_last_dimension_index_data()
        xdata_valid_idxs = ~np.isnan(xdata)

        xdata = xdata[xdata_valid_idxs]
        ydata = ydata[xdata_valid_idxs]
        #
        booldata, codes = toc.get_int_from_log(xdata)
        #
        canvas = self.get_canvas()

        toc_uid = UIM._getparentuid(self._controller_uid)
        track_controller_uid = UIM._getparentuid(toc_uid)
        track_controller = UIM.get(track_controller_uid)
        #
        for i, code in enumerate(codes):
            vec = []
            start = None
            end = None

            for idx in range(len(ydata)):
                d = booldata[i, idx]
                if d and start is None:
                    start = ydata[idx]
                elif not d and start is not None:
                    end = ydata[idx]
                    vec.append((start, end))
                    start = None

            patches = []
            for start, end in vec:
                patch = track_controller.append_artist('Rectangle', (0.0, start),
                                                       160.0, end - start
                                                       )
                patches.append(patch)
            collection = track_controller.append_artist('PatchCollection',
                                                        patches,
                                                        color=COLOR_CYCLE_NAMES[i]
                                                        )
            print(COLOR_CYCLE_NAMES[i])
            self._set_picking(collection, 0)
            self._mplot_objects[('part', code)] = collection

        self.draw_canvas()
