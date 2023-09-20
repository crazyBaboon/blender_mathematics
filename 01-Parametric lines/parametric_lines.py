import bpy
import numpy as np

# Set time 't' axis
t = np.arange(1.05, 5, 0.01)

# Set curve coordinates
points = np.zeros((len(t), 3))

for N in range(len(t)):
    x = 0.32*(1 - t[N]) * np.cos(10 * t[N])
    y = 0.32*(1 - t[N]) * np.sin(10 * t[N])
    z = 2.6-0.6*t[N]
    points[N] = [x, y, z]

# Create the curve and set its points
curve_data = bpy.data.curves.new(name='ParametricLine', type='CURVE')

polyline = curve_data.splines.new('POLY')
polyline.points.add(len(points) - 1)

for N in range(len(points)):
    x, y, z = points[N]
    polyline.points[N].co = (x, y, z, 1)

curve_object = bpy.data.objects.new('ParametricLine', curve_data)
bpy.context.collection.objects.link(curve_object)

