import bpy
from math import radians, sin, cos, cosh, ceil, floor
from numpy import exp, pi, arange, zeros, array
from mathutils import Vector, Matrix
import bmesh

######## RENDER PROPERTIES #####################

bpy.context.scene.cycles.tile_size = 256
bpy.context.scene.render.engine = 'CYCLES'; 
bpy.context.scene.cycles.samples = 2; 
bpy.context.scene.cycles.use_denoising = True

######## COLORMAP PROPERTIES ##################

# choose between "Jet", "Viridis", "90s" colormap
colormap = "Jet"
# display contour plot levels
display_levels = False

######## AXIS PROPERTIES ##################

# Set plot flags and properties:
title_plot = "Example of vector field"
display_grid = True
display_tick = True
label_x_axis = "X(m)"
label_y_axis = "Y(m)"
label_z_axis = "Z(m)"
thickness_x_axis = 0.01
thickness_y_axis = 0.01
thickness_z_axis = 0.01
colour_x_axis = (0.1, 0.1, 0.1, 1)
colour_y_axis = (0.1, 0.1, 0.1, 1)
colour_z_axis = (0.1, 0.1, 0.1, 1)
XoY_color = (0.973, 0.973, 0.973, 1)
YoZ_color = (0.961, 0.961, 0.961, 1)
XoZ_color = (0.949, 0.949, 0.949, 1)
xlim = (-2, 2)
ylim = (-2, 2)
zlim = (-1, 1)

# Calculate mins and maxes: 
max_x = xlim[1]
max_y = ylim[1]
max_z = zlim[1]
min_x = xlim[0]
min_y = ylim[0]
min_z = zlim[0]
 
def align_perpendicular_to_camera(object, camera):
    view_vector = camera.matrix_world.to_quaternion() @ Vector((0, 0, 1))
    object.rotation_euler = view_vector.to_track_quat('Z', 'Y').to_euler()
    bpy.context.view_layer.update()

def create_diffuse_material(mesh, colour, name):
    material = bpy.data.materials.new(name = name)
    material.diffuse_color = colour
    mesh.data.materials.append(material)

def normalize_function_values_1(value):
    normalized_data = (value - min_z) / (max_z - min_z)
    return normalized_data

def normalize_function_values_2(value):
    normalized_data = 2*((value - min_z) / (max_z - min_z)) - 1
    return normalized_data

def color_map(value, colormap, display_levels):
    if (colormap == "Viridis" and display_levels == False):
        value = normalize_function_values_2(value)
        color = [0.9*exp(-((value - 1)**2)/0.08) + 0.6*exp(-((value - 0.4)**2)/0.12),
        0.5*exp(-((value + 1)**2)/0.08) + 0.5*exp(-((value+0.5)**2)/0.2) + 0.6* exp(-((value )**2)/0.08) + 0.9*exp(-((value - 1)**2)/0.08) + 0.4*exp(-((value - 0.5)**2)/0.08), 
        exp(-((value + 1)**2)/0.08)  + 0.8*exp(-((value+0.5)**2)/0.08)   + 0.5*exp(-((value)**2)/0.08 ), 1]
    if (colormap == "90s" and display_levels == False):
        value = normalize_function_values_2(value)
        color = [0.9*exp(-((value-1)**2)/0.08) + 0.5*exp(-((value)**2)/0.02) +  0.55*exp(-((value-0.5)**2)/0.08),
        0.99*exp(-((value)**2)/0.08) + 0.8* exp(-((value - 0.6)**2)/0.08) + 0.5* exp(-((value + 0.35)**2)/0.02), 
        exp(-((value+0.5)**2)/0.08) + 0.5*exp(-((value)**2)/0.02), 1]
    
    # Jet colormap was adapted from Matplotlib: https://github.com/matplotlib/matplotlib/blob/main/lib/matplotlib/_cm.py
    if (colormap == "Jet" and display_levels == False):
        value = normalize_function_values_1(value)
        if (value < 0.11):
            color = [0,0,((1 - 0.5)/(0.11 - 0)) * value + (1 - ((1 - 0.5)/(0.11 - 0))*0.11),1]
        elif (value < 0.125):
            color = [0,(value - 0.125) / (0.375 - 0.125),1,1]    
        elif (value < 0.34):
            color = [0,(value - 0.125) / (0.375 - 0.125),1,1]   
        elif (value < 0.35):
              color = [0,
              (value - 0.125) / (0.375 - 0.125),
              ((0 - 1) / (0.65 - 0.34)) * value + (1 - ((0 - 1) / (0.65 - 0.34)) * 0.34),1]
        elif (value < 0.375):
              color = [(value - 0.35) / (0.66 - 0.35),
              (value - 0.125) / (0.375 - 0.125),
              ((0 - 1) / (0.65 - 0.34)) * value + (1 - ((0 - 1) / (0.65 - 0.34)) * 0.34),1]
        elif (value < 0.64):
              color = [(value - 0.35) / (0.66 - 0.35),
              1,
              ((0 - 1) / (0.65 - 0.34)) * value + (1 - ((0 - 1) / (0.65 - 0.34)) * 0.34),1]
        elif (value < 0.90):
              color = [1,
              1 - (value - 0.64) / (0.91 - 0.64),
              0,1]
        else:
              color = [ ((0.5 - 1.0)/(1 - 0.89)) * value + (0.5 - ((0.5 - 1.0)/(1 - 0.89)) *1.0),
              0,
              0,
              1]
    return color

def set_white_background():
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.render.film_transparent = True
    bpy.context.scene.view_settings.view_transform = 'Standard'
    bpy.context.scene.use_nodes = True
    alpha_over_node = bpy.context.scene.node_tree.nodes.new(type='CompositorNodeAlphaOver')
    # Connect composite nodes
    render_layers_node = bpy.context.scene.node_tree.nodes.get('Render Layers')
    composite_node = bpy.context.scene.node_tree.nodes.get('Composite')
    if render_layers_node and composite_node:
        bpy.context.scene.node_tree.links.new(render_layers_node.outputs['Image'], alpha_over_node.inputs[2])
        bpy.context.scene.node_tree.links.new(alpha_over_node.outputs[0], composite_node.inputs['Image'])
    # Set this thing to 1
    alpha_over_node.premul = 1

def create_axis_2D(axis, colour, thickness, display_grid, display_tick, xlim, ylim, zlim, label, XoY_color, YoZ_color, XoZ_color):
    bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=1)
    bpy.ops.transform.resize(value=(thickness, thickness, thickness))

    if (axis == 'X'):
        bpy.ops.transform.rotate(value=radians(90), orient_axis='Y')
        bpy.ops.transform.resize(value=((xlim[1]-xlim[0])/thickness, 1, 1))
        # Set X-axis colour
        axis_cilinder = bpy.context.active_object
        create_diffuse_material(axis_cilinder, colour, "axis_material")  
        #Add axis arrow
        bpy.ops.mesh.primitive_cone_add(radius1=1, radius2=0, depth=3)
        bpy.ops.transform.rotate(value=-radians(90), orient_axis='Y')
        bpy.ops.transform.translate(value=(xlim[1], 0, 0))
        bpy.ops.transform.resize(value=(3*thickness, 3*thickness, 3*thickness))
        # Set cone colour
        cone = bpy.context.active_object
        create_diffuse_material(cone, colour, "cone_material")

        # Round off x coords used for text and grid lines:
        if (xlim[0] > 0):
            xmin = floor(xlim[0]*10)/10
        else:
            xmin = ceil(xlim[0]*10)/10

        if (xlim[1] > 0):
            xmax = floor(xlim[1]*10)/10
        else:
            xmax = ceil(xlim[1]*10)/10
            
        xstep = (xmax - xmin)/4

        if display_tick == True:
            # Add the axis labels text:
            for N in range(1,5):   
                bpy.ops.object.text_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
                obj = bpy.context.active_object
                obj.location.x = xmin + xstep*N + 0.02
                obj.location.y = ylim[1] + 0.2
                obj.location.z = zlim[0] - 0.1
                text_data = obj.data
                text_data.body = str(round((xmin + xstep*N)*10)/10)    
                text_data.size = 0.12
                text = bpy.context.active_object
                create_diffuse_material(text, (0, 0, 0, 1), "text_material")
                
        # Create 'ylabel':
        bpy.ops.object.text_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        obj = bpy.context.active_object
        obj.location.x = 0.5*(xlim[1]+xlim[0]) * (0.95 + len(label)/10)
        obj.location.y = ylim[1] + 0.3
        obj.location.z = 0
        text_data = obj.data
        text_data.body = label   
        text_data.size = 0.13
        text = bpy.context.active_object
        #align_perpendicular_to_camera(text, bpy.data.objects.get("Camera"))
        create_diffuse_material(text, (0, 0, 0, 1), "text_material")
        
        
        #Add the auxaliary grid lines:
        if display_grid == True:
            for N in range(1,5):
                bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
                bpy.ops.transform.resize(value=(0.5*thickness, ylim[1]-ylim[0], 1))                
                bpy.ops.transform.translate(value=(xmin + xstep*N, (ylim[1]+ylim[0])*0.5, 0)) 
                line = bpy.context.active_object
                create_diffuse_material(line, (0.1, 0.1, 0.1, 1), "line_material")
            
            # Add the plane XoY:
            bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
            bpy.ops.transform.resize(value=(xlim[1]-xlim[0], ylim[1]-ylim[0], 1))                
            bpy.ops.transform.translate(value=(0.5*(xlim[1]+xlim[0]), 0.5*(ylim[1]+ylim[0]), 0))
            plane = bpy.context.active_object
            create_diffuse_material(plane, XoY_color, "plane_material")
                            
    elif (axis == 'Y'):  
        bpy.ops.transform.rotate(value=radians(90), orient_axis='X')
        bpy.ops.transform.resize(value=(1, (ylim[1]-ylim[0])/thickness, 1))
        # Set the X-axis to red
        axis_cilinder = bpy.context.active_object
        create_diffuse_material(axis_cilinder, colour, "axis_material")         
        #Add axis arrow
        bpy.ops.mesh.primitive_cone_add(radius1=1, radius2=0, depth=2)
        bpy.ops.transform.rotate(value=radians(90), orient_axis='X')
        bpy.ops.transform.translate(value=(0, ylim[1], 0))
        bpy.ops.transform.resize(value=(3*thickness, 3*thickness, 3*thickness))
        # Set the cone to red
        cone = bpy.context.active_object
        create_diffuse_material(cone, colour, "cone_material")   

        # Round off y coords used for text and grid lines:
        if (ylim[0] > 0):
            ymin = floor(ylim[0]*10)/10
        else:
            ymin = ceil(ylim[0]*10)/10

        if (ylim[1] > 0):
            ymax = floor(ylim[1]*10)/10
        else:
            ymax = ceil(ylim[1]*10)/10
            
        ystep = (ymax - ymin)/4

        if display_tick == True:
            # Add the Y-axis labels text:
            for N in range(1,5):   
                bpy.ops.object.text_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
                obj = bpy.context.active_object
                obj.location.x = xlim[1] + 0.02
                obj.location.y = ymin + ystep*N
                obj.location.z = 0
                text_data = obj.data
                text_data.body = str(round((ymin + ystep*N)*10)/10)    
                text_data.size = 0.12
                text = bpy.context.active_object
                create_diffuse_material(text, (0, 0, 0, 1), "text_material")

        # Create 'xlabel':
        bpy.ops.object.text_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        obj = bpy.context.active_object
        obj.location.x = xlim[1] + 0.07
        obj.location.y = 0.5*(ylim[1]+ylim[0])+0.2
        obj.location.z = 0
        text_data = obj.data
        text_data.body = label   
        text_data.size = 0.13
        text = bpy.context.active_object
        create_diffuse_material(text, (0, 0, 0, 1), "text_material")


        #Add the auxaliary grid lines:
        if display_grid == True:
            for N in range(1,5): 
                bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
                bpy.ops.transform.resize(value=(xlim[1]-xlim[0], 0.5*thickness, 1))                
                bpy.ops.transform.translate(value=((xlim[1]+xlim[0])*0.5, ymin + ystep*N, 0)) 
                line = bpy.context.active_object
                create_diffuse_material(line, (0.1, 0.1, 0.1, 1), "line_material")



def set_title(label):
    bpy.ops.object.text_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    obj = bpy.context.active_object
    obj.location.x = xlim[0] + 1.2
    obj.location.y = ylim[1] + 0.8
    obj.location.z = 0
    text_data = obj.data
    text_data.body = label    
    text_data.size = 0.15
    text = bpy.context.active_object
    create_diffuse_material(text, (0, 0, 0, 1), "text_material")

def draw_vector(start_point, direction, length, thickness, colour):
    bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=1)
    bpy.ops.transform.resize(value=(thickness, thickness, 0.5*length))
    bpy.ops.transform.translate(value=(start_point[0], start_point[1], start_point[2]))
    cylinder = bpy.context.object
    cylinder.name = "vector.body"
    direction = Vector(direction).normalized()
    
    # Set the orientation of the vector cilinder
    rot_quat = direction.to_track_quat('Z', 'Y')
    cylinder.rotation_euler = rot_quat.to_euler()

    # Set the colour for the vector cilinder
    vector_cilinder = bpy.context.active_object
    create_diffuse_material(vector_cilinder, colour, "vector_material")  
    # Add vector arrow
    bpy.ops.mesh.primitive_cone_add(radius1=30*thickness, radius2=0, depth=60*thickness)
    bpy.ops.transform.translate(value=(start_point[0] + direction[0] * 0.4 * length, 
                                       start_point[1] + direction[1] * 0.4 * length, 
                                       start_point[2] + direction[2] * 0.4 * length))
    bpy.ops.transform.resize(value=(10*thickness, 10*thickness, 10*thickness))
    cone = bpy.context.object
    cone.name = "vector.head"
    direction = Vector(direction).normalized()
    
    # Set the orientation of the Arrow
    rot_quat = direction.to_track_quat('Z', 'Y')
    cone.rotation_euler = rot_quat.to_euler()
    # Set the arrow colour
    cone = bpy.context.active_object
    create_diffuse_material(cone, colour, "cone_material")    

def differentiate (x1, x2, dt):
    return (x1 - x2)/dt

# Set ambient light colour
bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = (0.80, 0.80, 0.80, 1)

# set the camera position and direction

#bpy.ops.view3d.view_persportho('INVOKE_DEFAULT')
# Set the view to the XY plane
#bpy.context.space_data.region_3d.view_perspective = 'ORTHO'
camera = bpy.data.objects.get("Camera")
camera.rotation_euler = (0, 0, 0)
camera.location.x = 0
camera.location.y = 0
camera.location.z = 15


set_white_background()


create_axis_2D('X', 
            colour_x_axis, 
            thickness_x_axis, 
            display_grid,
            display_tick, 
            xlim, 
            ylim, 
            zlim,
            label_y_axis,
            XoY_color,
            YoZ_color,
            XoZ_color) 

create_axis_2D('Y', 
            colour_y_axis, 
            thickness_y_axis, 
            display_grid,
            display_tick,  
            xlim, 
            ylim, 
            zlim,
            label_x_axis,
            XoY_color,
            YoZ_color,
            XoZ_color) 

set_title(title_plot)




 
#### NOW CREATE THE 2D VECTOR PLOT ANIMATION ################

# Set time 't' axis
dt = 0.005
t = arange(-6, 6, dt)
num_points = len(t)

# Allocate space for curve coordinates
points_0 = zeros((len(t), 3))
points_1 = zeros((len(t), 3))
points_2 = zeros((len(t), 3))
points_3 = zeros((len(t), 3))
points_4 = zeros((len(t), 3))
points_5 = zeros((len(t), 3))
points_6 = zeros((len(t), 3))
points_7 = zeros((len(t), 3))
points_8 = zeros((len(t), 3))
points_9 = zeros((len(t), 3))
points_10 = zeros((len(t), 3))
points_11 = zeros((len(t), 3))
points_12 = zeros((len(t), 3))
points_13 = zeros((len(t), 3))
points_14 = zeros((len(t), 3))
points_15 = zeros((len(t), 3))
points_16 = zeros((len(t), 3))
points_17 = zeros((len(t), 3))
points_18 = zeros((len(t), 3))
points_19 = zeros((len(t), 3))
points_20 = zeros((len(t), 3))
points_21 = zeros((len(t), 3))
points_22 = zeros((len(t), 3))
points_23 = zeros((len(t), 3))
points_24 = zeros((len(t), 3))
points_25 = zeros((len(t), 3))
points_26 = zeros((len(t), 3))
points_27 = zeros((len(t), 3))

# Define family of lines x(t),y(t),z(t) equations that will be part of the vector field:
for N in range(len(t)):
    x = t[N]
    y_0 = exp(t[N]+2 )
    y_1 = exp(t[N]+1.5)
    y_2 = exp(t[N]+1)
    y_3 = exp(t[N]+0.5)
    y_4 = exp(t[N]) 
    y_5 = exp(t[N]-0.5) 
    y_6 = exp(t[N]-1)
    y_7 = exp(t[N]-1.5)
    y_8 = exp(t[N]-2) 
    y_9 = exp(t[N]-2.5)
    y_10 = exp(t[N]-3)
    y_11 = exp(t[N]-3.5)
    y_12 = exp(t[N]-4)
    y_13 = exp(t[N]-4.5)
    y_14 = -exp(t[N]+2 )
    y_15 = -exp(t[N]+1.5)
    y_16 = -exp(t[N]+1)
    y_17 = -exp(t[N]+0.5)
    y_18 = -exp(t[N]) 
    y_19 = -exp(t[N]-0.5) 
    y_20 = -exp(t[N]-1)
    y_21 = -exp(t[N]-1.5)
    y_22 = -exp(t[N]-2) 
    y_23 = -exp(t[N]-2.5)
    y_24 = -exp(t[N]-3)
    y_25 = -exp(t[N]-3.5)
    y_26 = -exp(t[N]-4)
    y_27 = -exp(t[N]-4.5)
    z = 0.1
    points_0[N] = [x, y_0, z]
    points_1[N] = [x, y_1, z]    
    points_2[N] = [x, y_2, z]
    points_3[N] = [x, y_3, z]
    points_4[N] = [x, y_4, z]
    points_5[N] = [x, y_5, z]
    points_6[N] = [x, y_6, z]
    points_7[N] = [x, y_7, z]    
    points_8[N] = [x, y_8, z]
    points_9[N] = [x, y_9, z]
    points_10[N] = [x, y_10, z]  
    points_11[N] = [x, y_11, z]
    points_12[N] = [x, y_12, z]
    points_13[N] = [x, y_13, z] 
    points_14[N] = [x, y_14, z]
    points_15[N] = [x, y_15, z]    
    points_16[N] = [x, y_16, z]
    points_17[N] = [x, y_17, z]
    points_18[N] = [x, y_18, z]
    points_19[N] = [x, y_19, z]
    points_20[N] = [x, y_20, z]
    points_21[N] = [x, y_21, z]    
    points_22[N] = [x, y_22, z]
    points_23[N] = [x, y_23, z]
    points_24[N] = [x, y_24, z]  
    points_25[N] = [x, y_25, z]
    points_26[N] = [x, y_26, z]
    points_27[N] = [x, y_27, z] 
     
        
all_points = [points_0, 
              points_1, 
              points_2, 
              points_3, 
              points_4, 
              points_5, 
              points_6, 
              points_7, 
              points_8, 
              points_9, 
              points_10, 
              points_11, 
              points_12,
              points_13,
              points_14, 
              points_15, 
              points_16, 
              points_17, 
              points_18, 
              points_19, 
              points_20, 
              points_21, 
              points_22, 
              points_23, 
              points_24, 
              points_25, 
              points_26,
              points_27]

num_lines = 28
unit_spacing_vectors = 50
num_vectors = 35

points_diff = [zeros((num_points - 1, 3)) for _ in range(len(all_points))]

## Automatically calculate the diff of whatever equation user has defined.
for i, points_set in enumerate(all_points):
    for N in range(num_points - 1):
        dx = -differentiate(points_set[N, 0], points_set[N+1, 0], dt)
        dy = -differentiate(points_set[N, 1], points_set[N+1, 1], dt)
        dz = -differentiate(points_set[N, 2], points_set[N+1, 2], dt)
        points_diff[i][N] = [dx, dy, dz]
   
max_animation_step = 301

length = 0.2
thickness = 0.01
colour = (0.1, 0.2, 1, 1)

for step in range(1, max_animation_step):
    camera.location.z = 0.1 + 15/(1 + exp(-0.08*step + 5)) # Sigmoid S-Shape
    
    for line  in range(num_lines):
        for N in range(num_vectors):

            start_point = (
                all_points[line][unit_spacing_vectors * N + step, 0],
                all_points[line][unit_spacing_vectors * N + step, 1],
                all_points[line][unit_spacing_vectors * N + step, 2]
            )

            direction = (
                points_diff[line][unit_spacing_vectors * N + step, 0],
                points_diff[line][unit_spacing_vectors * N + step, 1],
                points_diff[line][unit_spacing_vectors * N + step, 2]
            )
            # draw the vector only if it lies between min_z and max_z
            if ((all_points[line][unit_spacing_vectors*N + step,1] > min_y and all_points[line][unit_spacing_vectors*N + step,1] < max_y)
            and (all_points[line][unit_spacing_vectors*N + step,0] > min_x and all_points[line][unit_spacing_vectors*N + step,0] < max_x)):
                draw_vector(start_point, direction, length, thickness, colour)
            
    # CHANGE THE NAME OF THE FILEPATH!!!
    bpy.context.scene.render.filepath = '/home/pinto/Pictures/I/New4/Frame_%d.jpg' % step
    bpy.ops.render.render(write_still=True);

    # Delete the vectors before next animation loop or else they will be drawn again:
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH' and (obj.name.startswith("vector.body") or obj.name.startswith("vector.head")):
            obj.select_set(True)

    bpy.ops.object.delete()
