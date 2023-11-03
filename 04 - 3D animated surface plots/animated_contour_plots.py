import bpy
from math import radians, sin, cos, ceil, floor
from numpy import exp, pi, arange
from mathutils import Vector
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
title_plot = "Normal mode (nx= 1, ny= 2)"
display_grid = True
display_tick = True
label_x_axis = "x(m)"
label_y_axis = "Y(m)"
label_z_axis = "Sound Pressure (Pa)"
thickness_x_axis = 0.01
thickness_y_axis = 0.01
thickness_z_axis = 0.01
colour_x_axis = (0.1, 0.1, 0.1, 1)
colour_y_axis = (0.1, 0.1, 0.1, 1)
colour_z_axis = (0.1, 0.1, 0.1, 1)
XoY_color = (0.973, 0.973, 0.973, 1)
YoZ_color = (0.961, 0.961, 0.961, 1)
XoZ_color = (0.949, 0.949, 0.949, 1)
xlim = (-1, 1)
ylim = (-1, 1)
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

bpy.ops.mesh.primitive_grid_add(x_subdivisions=100, y_subdivisions=100,  location=(0, 0, 0))
bpy.ops.transform.resize(value=(1, 1, 1))

t = arange(0, 3, 0.0001)

max_step = 120;

for step in range(1, max_step):
    
    bpy.ops.object.mode_set(mode='EDIT')
    
    obj = bpy.context.active_object
    mesh = obj.data

    bm = bmesh.from_edit_mesh(mesh)
    for v in bm.verts:
        x = v.co.x
        y = v.co.y
        z = (cos(1*pi*(x+1)/2) * cos(2*pi*(y+1)/2)) * sin(2 * pi * 200 * t[step]) # Attention!! Coordinate translation is necessary!
        #z = (0.00005/t[step])*exp(-(x**2 + y**2) / (0.2)) / ((0.2) * pi)
        v.co.z = z

    bmesh.update_edit_mesh(mesh)

    bpy.ops.object.mode_set(mode='OBJECT')

    # Switch to Vertex Paint mode
    bpy.ops.object.mode_set(mode='VERTEX_PAINT')

    # Set the active vertex color layer
    active_vc_layer = obj.data.vertex_colors.active
    if active_vc_layer is None:
        active_vc_layer = obj.data.vertex_colors.new()

    # Loop through the vertices and set them to red
    for poly in obj.data.polygons:
        for loop_index in poly.loop_indices:
            loop = obj.data.loops[loop_index]
            vertex_index = loop.vertex_index
            vert = mesh.vertices[vertex_index]
            color = color_map(vert.co.z, colormap, display_levels)
    #            color = [4*abs(vert.co.z), 0, 0, 1]  # Red color (RGBA)
    #        else:
    #            color = [0, 0, 4*abs(vert.co.z), 1]  # Red color (RGBA)
            active_vc_layer.data[loop_index].color = color

    # Create a new material
    mat = bpy.data.materials.new(name="Vertex Color Material")
    obj.data.materials.append(mat)

    # Get a reference to the material
    mat = obj.data.materials[0]

    # Create a new node tree for the material
    mat.use_nodes = True
    nodes = mat.node_tree.nodes

    # Clear default nodes
    for node in nodes:
        nodes.remove(node)

    # Add a Vertex Color node
    vc_node = nodes.new(type='ShaderNodeVertexColor')
    vc_node.layer_name = 'Attribute'
    vc_node.location = (0,0)  # Optional: Set the location of the node

    # Add a Principled BSDF shader node
    bsdf_node = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf_node.location = (400,0)  # Optional: Set the location of the node

    # Add an Output node
    output_node = nodes.new(type='ShaderNodeOutputMaterial')
    output_node.location = (600,0)  # Optional: Set the location of the node

    # Connect the nodes
    mat.node_tree.links.new(vc_node.outputs["Color"], bsdf_node.inputs["Base Color"])
    mat.node_tree.links.new(bsdf_node.outputs["BSDF"], output_node.inputs["Surface"])

    bpy.ops.object.mode_set(mode='OBJECT')

    bpy.context.scene.render.filepath = '/home/pinto/Pictures/G/vr_shot_%d.jpg' % step
    bpy.ops.render.render(write_still=True);


