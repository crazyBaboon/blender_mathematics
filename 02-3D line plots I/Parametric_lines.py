import bpy
import numpy as np

def create_diffuse_material(mesh, colour, name):
    material = bpy.data.materials.new(name = name)
    material.diffuse_color = colour
    mesh.data.materials.append(material)

# Set time 't' axis
t = np.arange(0, 2, 0.001)

# Set curve coordinates
points = np.zeros((len(t), 3))

for N in range(len(t)):
    x = 1*np.cos(20 * t[N])+1
    y = 1*np.sin(20 * t[N])+1
    z = t[N]
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

# paint the line colour 'red'
create_diffuse_material(curve_object, (0.869, 0.032, 0.016, 1), "line_material")

# Give thickness to the line so it can be rendered
curve_object.data.bevel_depth = 0.01

