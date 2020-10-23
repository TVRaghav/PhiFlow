from typing import Any

from phi import math
from phi.geom import Geometry, GridCell, Box
from ._field import SampledField
from ._grid import CenteredGrid


class PointCloud(SampledField):

    def __init__(self, elements: Geometry, values: Any=1, extrapolation=math.extrapolation.ZERO, add_overlapping=False):
        """
        A point cloud consists of elements at arbitrary locations.
        A value or vector is associated with each element.

        Outside of elements, the value of the field is determined by the extrapolation.

        :param elements: Geometry object specifying the sample points and sizes
        :param values: values corresponding to elements
        :param extrapolation: values outside elements
        :param add_overlapping: True: values of overlapping geometries are summed. False: values between overlapping geometries are interpolated
        """
        SampledField.__init__(self, elements, values, extrapolation)
        self._add_overlapping = add_overlapping

    def sample_at(self, points, reduce_channels=()):
        if isinstance(points, GridCell):
            return self._grid_scatter(points.bounds, points.resolution)
        else:
            raise NotImplementedError()

    def _grid_scatter(self, box: Box, resolution: math.Shape):
        """
        Approximately samples this field on a regular grid using math.scatter().

        :param box: physical dimensions of the grid
        :param resolution: grid resolution
        :return: CenteredGrid
        """
        closest_index = math.to_int(math.round(box.global_to_local(self.points) * resolution))
        scattered = math.scatter(self.sample_points, valid_indices, self.values, shape, duplicates_handling=self.mode)
        return CenteredGrid(scattered, box, self.extrapolation)

    def mask(self):
        return PointCloud(self._elements, 1, math.extrapolation.ZERO, add_overlapping=False)

    def __repr__(self):
        return "PointCloud[%s at %s]" % (self._values, self._elements)


def _distribute_points(density, particles_per_cell=1, distribution='uniform'):
    """
Distribute points according to the distribution specified in density.
    :param density: binary tensor
    :param particles_per_cell: integer
    :param distribution: 'uniform' or 'center'
    :return: tensor of shape (batch_size, point_count, rank)
    """
    assert distribution in ('center', 'uniform')
    index_array = []
    batch_size = math.staticshape(density)[0] if math.staticshape(density)[0] is not None else 1
    
    for batch in range(batch_size):
        indices = math.where(density[batch, ..., 0] > 0)
        indices = math.to_float(indices)

        temp = []
        for _ in range(particles_per_cell):
            if distribution == 'center':
                temp.append(indices + 0.5)
            elif distribution == 'uniform':
                temp.append(indices + math.random_uniform(math.shape(indices)))
        index_array.append(math.concat(temp, axis=0))
    try:
        index_array = math.stack(index_array)
        return index_array
    except ValueError:
        raise ValueError("all arrays in the batch must have the same number of active cells.")
