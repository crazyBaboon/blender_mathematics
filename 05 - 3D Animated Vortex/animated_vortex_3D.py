import bpy
from math import radians, sin, cos, cosh, ceil, floor
from numpy import exp, pi, arange, zeros
from mathutils import Vector, Matrix
import bmesh

######## REDER PROPERTIES #####################

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
title_plot = "Atmospheric disturbance"
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

def create_axis(axis, colour, thickness, display_grid, display_tick, xlim, ylim, zlim, label, XoY_color, YoZ_color, XoZ_color):
    bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=1)
    bpy.ops.transform.resize(value=(thickness, thickness, thickness))

    if (axis == 'X'):
        bpy.ops.transform.rotate(value=radians(90), orient_axis='Y')
        bpy.ops.transform.resize(value=((xlim[1]-xlim[0])/thickness, 1, 1))
        bpy.ops.transform.translate(value=(0.5*(xlim[1]+xlim[0]), ylim[0], zlim[0]))
        # Set the X-axis to red
        axis_cilinder = bpy.context.active_object
        create_diffuse_material(axis_cilinder, colour, "axis_material")  
        #Add axis arrow
        bpy.ops.mesh.primitive_cone_add(radius1=1, radius2=0, depth=3)
        bpy.ops.transform.rotate(value=-radians(90), orient_axis='Y')
        bpy.ops.transform.translate(value=(xlim[1], ylim[0], zlim[0]))
        bpy.ops.transform.resize(value=(3*thickness, 3*thickness, 3*thickness))
        # Set the cone to red
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
                obj.location.y = ylim[1] + 0.05
                obj.location.z = zlim[0] - 0.1
                text_data = obj.data
                text_data.body = str(round((xmin + xstep*N)*10)/10)    
                text_data.size = 0.12
                text = bpy.context.active_object
                align_perpendicular_to_camera(text, bpy.data.objects.get("Camera"))
                create_diffuse_material(text, (0, 0, 0, 1), "text_material")
                
        # Create 'xlabel':
        bpy.ops.object.text_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        obj = bpy.context.active_object
        obj.location.x = 0.5*(xlim[1]+xlim[0]) * (0.95 + len(label)/10)
        obj.location.y = ylim[1] + 0.05
        obj.location.z = zlim[0] - 0.3
        text_data = obj.data
        text_data.body = label   
        text_data.size = 0.13
        text = bpy.context.active_object
        align_perpendicular_to_camera(text, bpy.data.objects.get("Camera"))
        create_diffuse_material(text, (0, 0, 0, 1), "text_material")
        
        
        #Add the auxaliary grid lines and corresponding planes:
        if display_grid == True:
            for N in range(1,5): # add the lines
                bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
                bpy.ops.transform.rotate(value=radians(90), orient_axis=axis)
                bpy.ops.transform.resize(value=(0.5*thickness, 0.5*thickness, zlim[1]-zlim[0]))
                bpy.ops.transform.translate(value=(xmin + xstep*N, ylim[0], (zlim[1]+zlim[0])*0.5 )) # anchor point
                line = bpy.context.active_object
                create_diffuse_material(line, (0.1, 0.1, 0.1, 1), "line_material")
                               
            for N in range(1,5):
                bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
                bpy.ops.transform.resize(value=(0.5*thickness, ylim[1]-ylim[0], 1))                
                bpy.ops.transform.translate(value=(xmin + xstep*N, (ylim[1]+ylim[0])*0.5, zlim[0])) 
                line = bpy.context.active_object
                create_diffuse_material(line, (0.1, 0.1, 0.1, 1), "line_material")
            
            # Add the plane XoY:
            bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
            bpy.ops.transform.resize(value=(xlim[1]-xlim[0], ylim[1]-ylim[0], 1))                
            bpy.ops.transform.translate(value=(0.5*(xlim[1]+xlim[0]), 0.5*(ylim[1]+ylim[0]), zlim[0]-0.01))
            plane = bpy.context.active_object
            create_diffuse_material(plane, XoY_color, "plane_material")
                            
    elif (axis == 'Y'):  
        bpy.ops.transform.rotate(value=radians(90), orient_axis='X')
        bpy.ops.transform.resize(value=(1, (ylim[1]-ylim[0])/thickness, 1))
        bpy.ops.transform.translate(value=(xlim[0], 0.5*(ylim[1]+ylim[0]), zlim[0]))
        # Set the X-axis to red
        axis_cilinder = bpy.context.active_object
        create_diffuse_material(axis_cilinder, colour, "axis_material")         
        #Add axis arrow
        bpy.ops.mesh.primitive_cone_add(radius1=1, radius2=0, depth=2)
        bpy.ops.transform.rotate(value=radians(90), orient_axis='X')
        bpy.ops.transform.translate(value=(xlim[0], ylim[1], zlim[0]))
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
                obj.location.y = ymin + ystep*N - 0.2
                obj.location.z = zlim[0] - 0.2
                text_data = obj.data
                text_data.body = str(round((ymin + ystep*N)*10)/10)    
                text_data.size = 0.12
                text = bpy.context.active_object
                align_perpendicular_to_camera(text, bpy.data.objects.get("Camera"))
                create_diffuse_material(text, (0, 0, 0, 1), "text_material")
                
        # Create 'ylabel':
        bpy.ops.object.text_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        obj = bpy.context.active_object
        obj.location.x = xlim[1] + 0.07
        obj.location.y = 0.5*(ylim[1]+ylim[0]) - 0.3
        obj.location.z = zlim[0] - 0.4
        text_data = obj.data
        text_data.body = label   
        text_data.size = 0.13
        text = bpy.context.active_object
        create_diffuse_material(text, (0, 0, 0, 1), "text_material")
        align_perpendicular_to_camera(text, bpy.data.objects.get("Camera"))
            
        #Add the auxaliary grid lines and corresponding planes:
        if display_grid == True:
            for N in range(1,5): # Add the lines
                bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
                bpy.ops.transform.rotate(value=radians(90), orient_axis=axis)
                bpy.ops.transform.resize(value=(0.5*thickness, 0.5*thickness, zlim[1]-zlim[0]))
                bpy.ops.transform.translate(value=(xlim[0], ymin + ystep*N, (zlim[1]+zlim[0])*0.5))
                line = bpy.context.active_object
                create_diffuse_material(line, (0.1, 0.1, 0.1, 1), "line_material")
                
            for N in range(1,5): 
                bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
                bpy.ops.transform.resize(value=(xlim[1]-xlim[0], 0.5*thickness, 1))                
                bpy.ops.transform.translate(value=((xlim[1]+xlim[0])*0.5, ymin + ystep*N, zlim[0])) 
                line = bpy.context.active_object
                create_diffuse_material(line, (0.1, 0.1, 0.1, 1), "line_material")
           
            # Add the plane YoZ:
            bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
            bpy.ops.transform.resize(value=(zlim[1]-zlim[0], ylim[1]-ylim[0], 1))    
            bpy.ops.transform.rotate(value=radians(90), orient_axis=axis)              
            bpy.ops.transform.translate(value=(xlim[0]-0.01, 0.5*(ylim[1]+ylim[0]), 0.5*(zlim[1]+zlim[0])))
            plane = bpy.context.active_object
            create_diffuse_material(plane, YoZ_color, "plane_material")   
                 
    elif (axis == 'Z'):  
        bpy.ops.transform.rotate(value=radians(90), orient_axis='Z')
        bpy.ops.transform.resize(value=(1, 1, (zlim[1]-zlim[0])/thickness))
        bpy.ops.transform.translate(value=(xlim[0], ylim[0], 0.5*(zlim[1]+zlim[0])))
        # Set the X-axis to red
        axis_cilinder = bpy.context.active_object
        create_diffuse_material(axis_cilinder, colour, "axis_material")         
        #Add axis arrow
        bpy.ops.mesh.primitive_cone_add(radius1=1, radius2=0, depth=2)
        bpy.ops.transform.rotate(value=radians(90), orient_axis=axis)
        bpy.ops.transform.translate(value=(xlim[0], ylim[0], zlim[1]))
        bpy.ops.transform.resize(value=(3*thickness, 3*thickness, 3*thickness))
        # Set the cone to red
        cone = bpy.context.active_object
        create_diffuse_material(cone, colour, "cone_material")

        # Round off z coords used for text and grid lines:
        if (zlim[0] > 0):
            zmin = floor(zlim[0]*10)/10
        else:
            zmin = ceil(zlim[0]*10)/10

        if (zlim[1] > 0):
            zmax = floor(zlim[1]*10)/10
        else:
            zmax = ceil(zlim[1]*10)/10

        zstep = (zmax - zmin)/4
        
        if display_tick == True:
            # Add the axis labels text:
            for N in range(1,5):   
                bpy.ops.object.text_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
                obj = bpy.context.active_object
                obj.location.x = xlim[1] + 0.05
                obj.location.y = ylim[0] - 0.3
                obj.location.z = zmin + zstep*N - 0.10
                text_data = obj.data
                text_data.body = str(round((zmin + zstep*N)*10)/10)    
                text_data.size = 0.12
                text = bpy.context.active_object
                align_perpendicular_to_camera(text, bpy.data.objects.get("Camera"))
                create_diffuse_material(text, (0, 0, 0, 1), "text_material")
            
        # Create 'zlabel':
        bpy.ops.object.text_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        obj = bpy.context.active_object
        obj.location.x = xlim[1] + 0.05
        obj.location.y = ylim[0]  - 0.7*(0.8 + len(label)/10)
        obj.location.z = 0.5*(zlim[1] + zlim[0]) * 1.1
        text_data = obj.data
        text_data.body = label    
        text_data.size = 0.13
        text = bpy.context.active_object
        align_perpendicular_to_camera(text, bpy.data.objects.get("Camera"))
        create_diffuse_material(text, (0, 0, 0, 1), "text_material")
                          
        #Add the auxaliary grid lines and corresponding planes:
        if display_grid == True:
            for N in range(1,4): #add the lines
                bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
                bpy.ops.transform.resize(value=(xlim[1]-xlim[0], 0.5*thickness, 1))
                bpy.ops.transform.translate(value=((xlim[1]+xlim[0])*0.5, ylim[0], zmin + zstep*N)) 
                line = bpy.context.active_object
                create_diffuse_material(line, (0.1, 0.1, 0.1, 1), "line_material")
                                    
            for N in range(1,4): 
                bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
                bpy.ops.transform.resize(value=(0.5*thickness, ylim[1]-ylim[0], 1))                
                bpy.ops.transform.translate(value=(xlim[0], (ylim[1]+ylim[0])*0.5, zmin + zstep*N))  
                line = bpy.context.active_object
                create_diffuse_material(line, (0.1, 0.1, 0.1, 1), "line_material")                            
            
            #add the XoZ plane:
            bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
            bpy.ops.transform.resize(value=(xlim[1]-xlim[0], zlim[1]-zlim[0], 1))  
            bpy.ops.transform.rotate(value=radians(90), orient_axis='X')              
            bpy.ops.transform.translate(value=(0.5*(xlim[1]+xlim[0]), ylim[0]-0.01, 0.5*(zlim[1]+zlim[0])))
            plane = bpy.context.active_object
            create_diffuse_material(plane, XoZ_color, "plane_material")   

def set_title(label):
    bpy.ops.object.text_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    obj = bpy.context.active_object
    obj.location.x = xlim[0] + 0.05
    obj.location.y = ylim[0] - 0.35
    obj.location.z = zlim[1] * 1.3
    text_data = obj.data
    text_data.body = label    
    text_data.size = 0.15
    text = bpy.context.active_object
    align_perpendicular_to_camera(text, bpy.data.objects.get("Camera"))
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
camera = bpy.data.objects.get("Camera")
camera.rotation_euler = (1.1938, 0, 2.1258)
camera.location.x = (zlim[1] - zlim[0])*1*13.8926 * cos(camera.rotation_euler.x) + (xlim[0] + xlim[1])/2
camera.location.y = (zlim[1] - zlim[0])*1*9.7476 * cos(camera.rotation_euler.x) + (ylim[0] + ylim[1])/2
camera.location.z = (zlim[1] - zlim[0])*1*6.336805 * cos(camera.rotation_euler.x) + (zlim[0] + zlim[1])/2

set_white_background()


create_axis('X', 
            colour_x_axis, 
            thickness_x_axis, 
            display_grid,
            display_tick, 
            xlim, 
            ylim, 
            zlim,
            label_x_axis,
            XoY_color,
            YoZ_color,
            XoZ_color) 

create_axis('Y', 
            colour_y_axis, 
            thickness_y_axis, 
            display_grid,
            display_tick,  
            xlim, 
            ylim, 
            zlim,
            label_y_axis,
            XoY_color,
            YoZ_color,
            XoZ_color) 

create_axis('Z', 
            colour_z_axis, 
            thickness_z_axis, 
            display_grid,
            display_tick, 
            xlim, 
            ylim, 
            zlim,
            label_z_axis,
            XoY_color,
            YoZ_color,
            XoZ_color) 

set_title(title_plot)
     
#### NOW CREATE THE 3D CONTOUR PLOT ANIMATION ################

# Set time 't' axis
dt = 0.001
t = arange(-1.5, 3, dt)

# Allocate space for curve coordinates
points = zeros((len(t), 3))
points_diff = zeros((len(t) - 1, 3))


# Define line x(t),y(t),z(t) equation:
for N in range(len(t)):
    x = (cosh(t[N])     * cos(10 * t[N]))* cos(2 * t[N])
    y = (cosh(1 - t[N]) * sin(10 * t[N]))* cos(2 * t[N])
    z = (t[N])* cos(0.2 * t[N])
    points[N] = [x, y, z]

# Automatically calculate the diff of whatever equation user has defined.
for N in range(len(t) - 1):
    dx = -differentiate(points[N, 0], points[N+1, 0], dt)
    dy = -differentiate(points[N, 1], points[N+1, 1], dt)
    dz = -differentiate(points[N, 2], points[N+1, 2], dt)
    points_diff[N] = [dx, dy, dz]
 

max_step = 150

length = 0.2
thickness = 0.01
colour = (0.1, 0.2, 1, 1)

for step in range(1, max_step):
       
    for N in range(160):
        # the 25*N represents a 25 unit spacing between vectors
        start_point = (points[25*N + step,0], 
                       points[25*N + step,1], 
                       points[25*N + step,2])
        direction = (points_diff[25*N+1 + step,0], 
                     points_diff[25*N+1 + step,1], 
                     points_diff[25*N+1 + step,2])
        # draw the vector if it lies between min_z and max_z
        if (points[25*N + step,2] > min_z and points[25*N + step,2] < max_z + 0.10):
            draw_vector(start_point, direction, length, thickness, colour)
    
    # CHANGE THE NAME OF THE FILEPATH!!!
    bpy.context.scene.render.filepath = '/home/pinto/Pictures/H/Frame_%d.jpg' % step
    bpy.ops.render.render(write_still=True);

    # Delete the vectors before next animation loop or else they will be drawn again:
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH' and (obj.name.startswith("vector.body") or obj.name.startswith("vector.head")):
            obj.select_set(True)

    bpy.ops.object.delete()
    

