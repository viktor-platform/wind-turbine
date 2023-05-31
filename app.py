from viktor import (
    ViktorController, 
    File,
)

from viktor.parametrization import (
    ViktorParametrization,
    GeoPointField,
    NumberField,
    Section,
    Lookup,
)


from viktor.views import (
    GeometryResult, 
    GeometryView,
    ImageResult,
    ImageView,
    MapResult,
    MapPoint,
    MapView,
)

from ambiance import Atmosphere
import matplotlib.pyplot as plt
from pathlib import Path
from io import StringIO
import numpy as np


class Parametrization(ViktorParametrization):
    #Location input
    location_input = Section('Location Inputs')
    location_input.point = GeoPointField('Draw a point')
    location_input.altitude = NumberField('Altitude', default=0, min=0, max=8850, suffix='m')
    #Wind turbine geometry
    geometry_input = Section('Geometry Inputs')
    geometry_input.radius = NumberField('Wind Turbine Radius', default=5, min=2, suffix='m')
    geometry_input.height = NumberField('Wind Turbine height', default=20, min=Lookup('geometry_input.radius'), suffix='m')
    #Performance
    performance_input = Section('Performance Inputs')
    performance_input.performance_coeff = NumberField('Performance Coefficient Cp', variant='slider', default=0.35, min=0.25, max=0.45, step=0.01)

class Controller(ViktorController):
    viktor_enforce_field_constraints = True 
    label = 'Wind turbine app'
    parametrization = Parametrization

    @MapView('Map view', duration_guess=1)
    def get_map_view(self, params, **kwargs):
        # Create some point using given location coordinates
        features = []
        if params.location_input.point:
            features.append(MapPoint.from_geo_point(params.location_input.point))
        return MapResult(features)

    @GeometryView("Geometry", up_axis='Y', duration_guess=1)
    def get_geometry_view(self, params, **kwargs):
        #load a model of the wind turbine
        geometry = File.from_path(Path(__file__).parent / "wind_turbine_model.glb")  # or .glTF
        return GeometryResult(geometry)
    
    @ImageView("Plot", duration_guess=1)
    def create_result(self, params, **kwargs):
        # initialize figure
        fig = plt.figure()
        plt.title('performance Plot')
        plt.xlabel('Incoming Windspeed [km/h]')
        plt.ylabel('Power produced [kW]')
        x = np.arange(0,100,1)
        swept_area = np.pi * ((params.geometry_input.radius)/4.)**2
        air_density = Atmosphere(params.location_input.altitude).density
        y = np.zeros(np.size(x))
        for i in np.arange(np.size(x)):
            if x[i] < 8:
                y[i] = 0
            else:
                y[i] = 0.5 * air_density * swept_area * params.performance_input.performance_coeff * ((x[i]-8)/3.6)**3/1000
        # save figure
        plt.plot(x, y)
        svg_data = StringIO()
        fig.savefig(svg_data, format='svg')
        plt.close()
        return ImageResult(svg_data)