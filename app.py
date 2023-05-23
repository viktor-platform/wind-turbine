from viktor import (ViktorController, 
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
    locationInput = Section('Location Inputs')
    locationInput.point = GeoPointField('Draw a point')
    locationInput.altitude = NumberField('Altitude [m]', default=0, min=0, max=8850)
    #Wind turbine geometry
    geometryInput = Section('Geometry Inputs')
    geometryInput.radius = NumberField('Wind Turbine Radius [m]', default=5, min=2)
    geometryInput.height = NumberField('Wind Turbine height [m]', default=20, min=Lookup('geometryInput.radius'))
    #Performance
    performanceInput = Section('Performance Inputs')
    performanceInput.performanceCoeff = NumberField('Performance Coefficient Cp (-)', variant='slider', default=0.35, min=0.25, max=0.45, step=0.01)

class Controller(ViktorController):
    viktor_enforce_field_constraints = True 
    label = 'Wind turbine app'
    parametrization = Parametrization

    @MapView('Map view', duration_guess=1)
    def get_map_view(self, params, **kwargs):
        # Create some point using given location coordinates
        features = []
        if params.locationInput.point:
            features.append(MapPoint.from_geo_point(params.locationInput.point))
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
        sweptArea = np.pi * ((params.geometryInput.radius)/4.)**2
        airDensity = Atmosphere(params.locationInput.altitude).density
        print(airDensity)
        y = np.zeros(np.size(x))
        for i in np.arange(np.size(x)):
            if x[i] < 8:
                y[i] = 0
            else:
                y[i] = 0.5 * airDensity * sweptArea * params.performanceInput.performanceCoeff * ((x[i]-8)/3.6)**3/1000
        # save figure
        plt.plot(x, y)
        svg_data = StringIO()
        fig.savefig(svg_data, format='svg')
        plt.close()
        return ImageResult(svg_data)