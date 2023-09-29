import bpy
import numpy as np
from math import radians, sin, cos, ceil, floor

def create_diffuse_material(mesh, colour, name):
    material = bpy.data.materials.new(name = name)
    material.diffuse_color = colour
    mesh.data.materials.append(material)

# Set time 't' axis
t = np.arange(0, 3, 0.001)

# Set curve coordinates
points = np.zeros((len(t), 3))

# Define line x(t),y(t),z(t) equation:
for N in range(len(t)):
    x = 0.52*(1 - t[N]) * cos(10 * t[N])
    y = 0.52*(1 - t[N]) * sin(10 * t[N])
    z = 1-0.6*t[N]
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

# paint the line colour 'blue'
create_diffuse_material(curve_object, (0.016, 0.032, 0.869, 1), "line_material")

# Give thickness to the line so it can be rendered
curve_object.data.bevel_depth = 0.01

# Iterate through the points and find min and max
max_x, max_y, max_z = points[0]
min_x, min_y, min_z = points[0]

for point in points:
    x, y, z = point
    max_x = max(max_x, x)
    max_y = max(max_y, y)
    max_z = max(max_z, z)
    min_x = min(min_x, x)
    min_y = min(min_y, y)
    min_z = min(min_z, z)

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

def create_axis(axis, colour, thickness, display_grid, display_tick, xlim, ylim, zlim, label):
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
                obj.location.y = ylim[0] + 0.05
                obj.location.z = zlim[0] + 0.05
                bpy.ops.transform.rotate(value=radians(-90), orient_axis=axis)
                bpy.ops.transform.rotate(value=radians(180), orient_axis='Z')
                text_data = obj.data
                # Set the content of the text data block
                text_data.body = str(round((xmin + xstep*N)*10)/10)    
                text_data.size = 0.13
                text = bpy.context.active_object
                create_diffuse_material(text, (0, 0, 0, 1), "text_material")
        # Create 'xlabel':
        bpy.ops.object.text_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        obj = bpy.context.active_object
        obj.location.x = xlim[1] * (0.95 + len(label)/10)
        obj.location.y = ylim[0] + 0.05
        obj.location.z = zlim[0] + 0.05
        bpy.ops.transform.rotate(value=radians(-90), orient_axis=axis)
        bpy.ops.transform.rotate(value=radians(180), orient_axis='Z')
        text_data = obj.data
        # Set the content of the text data block
        text_data.body = label   
        text_data.size = 0.13
        text = bpy.context.active_object
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
            create_diffuse_material(plane, (0.973, 0.973, 0.973, 1), "plane_material")
                            
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
            # Add the axis labels text:
            for N in range(1,5):   
                bpy.ops.object.text_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
                obj = bpy.context.active_object
                obj.location.x = xlim[0] + 0.05
                obj.location.y = ymin + ystep*N - 0.2
                obj.location.z = zlim[0] + 0.05
                bpy.ops.transform.rotate(value=radians(-90), orient_axis='X')
                bpy.ops.transform.rotate(value=radians(-90), orient_axis='Z')
                text_data = obj.data
                # Set the content of the text data block
                text_data.body = str(round((ymin + ystep*N)*10)/10)    
                text_data.size = 0.13
                text = bpy.context.active_object
                create_diffuse_material(text, (0, 0, 0, 1), "text_material")
                
        # Create 'ylabel':
        bpy.ops.object.text_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        obj = bpy.context.active_object
        obj.location.x = xlim[0] + 0.05
        obj.location.y = ylim[1] * 1.08
        obj.location.z = zlim[0] + 0.05
        bpy.ops.transform.rotate(value=radians(-90), orient_axis='X')
        bpy.ops.transform.rotate(value=radians(-90), orient_axis='Z')
        text_data = obj.data
        # Set the content of the text data block
        text_data.body = label   
        text_data.size = 0.13
        text = bpy.context.active_object
        create_diffuse_material(text, (0, 0, 0, 1), "text_material")
            
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
            create_diffuse_material(plane, (0.961, 0.961, 0.961, 1), "plane_material")   
                 
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
                obj.location.x = xlim[0] + 0.05
                obj.location.y = ylim[0] + 0.05
                obj.location.z = zmin + zstep*N - 0.10
                bpy.ops.transform.rotate(value=radians(-90), orient_axis='X')
                bpy.ops.transform.rotate(value=radians(-90), orient_axis='Z')
                text_data = obj.data
                # Set the content of the text data block
                text_data.body = str(round((zmin + zstep*N)*10)/10)    
                text_data.size = 0.13
                text = bpy.context.active_object
                create_diffuse_material(text, (0, 0, 0, 1), "text_material")
            
        # Create 'zlabel':
        bpy.ops.object.text_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        obj = bpy.context.active_object
        obj.location.x = xlim[0] + 0.05
        obj.location.y = ylim[0] + 0.05
        obj.location.z = zlim[1] * 1.1
        bpy.ops.transform.rotate(value=radians(-90), orient_axis='X')
        bpy.ops.transform.rotate(value=radians(-90), orient_axis='Z')
        text_data = obj.data
        # Set the content of the text data block
        text_data.body = label    
        text_data.size = 0.13
        text = bpy.context.active_object
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
            create_diffuse_material(plane, (0.949, 0.949, 0.949, 1), "plane_material")   

def set_title(label):
    bpy.ops.object.text_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    obj = bpy.context.active_object
    obj.location.x = xlim[0] + 0.05
    obj.location.y = ylim[0] - 0.35
    obj.location.z = zlim[1] * 1.4
    bpy.ops.transform.rotate(value=radians(-90), orient_axis='X')
    bpy.ops.transform.rotate(value=radians(-120), orient_axis='Z')
    text_data = obj.data
    # Set the content of the text data block
    text_data.body = label    
    text_data.size = 0.15
    text = bpy.context.active_object
    create_diffuse_material(text, (0, 0, 0, 1), "text_material")

    


# Set ambient light colour
bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = (0.80, 0.80, 0.80, 1)

# Calculate min, max limits of the current plot
xlim = (min_x, max_x)
ylim = (min_y, max_y)
zlim = (min_z, max_z)

# set the camera position and direction
camera = bpy.data.objects.get("Camera")
camera.rotation_euler = (1.1938, 0, 2.1258)
camera.location.x = (zlim[1] - zlim[0])*0.8*13.8926 * cos(camera.rotation_euler.x) + (xlim[0] + xlim[1])/2
camera.location.y = (zlim[1] - zlim[0])*0.8*9.7476 * cos(camera.rotation_euler.x) + (ylim[0] + ylim[1])/2
camera.location.z = (zlim[1] - zlim[0])*0.8*6.336805 * cos(camera.rotation_euler.x) + (zlim[0] + zlim[1])/2

set_white_background()

# Set plot flags:
display_grid = True
display_tick = True 

create_axis(axis='X', 
            colour=(0.1, 0.1, 0.1, 1), 
            thickness = 0.01, 
            display_grid = display_grid,
            display_tick = display_tick, 
            xlim = xlim, 
            ylim = ylim, 
            zlim = zlim,
            label = "x[km]") 

create_axis(axis='Y', 
            colour=(0.1, 0.1, 0.1, 1), 
            thickness = 0.01, 
            display_grid = display_grid,
            display_tick = display_tick,  
            xlim = xlim, 
            ylim = ylim, 
            zlim = zlim,
            label = "y[km]") 

create_axis(axis='Z', 
            colour=(0.1, 0.1, 0.1, 1), 
            thickness = 0.01, 
            display_grid = display_grid,
            display_tick = display_tick, 
            xlim = xlim, 
            ylim = ylim, 
            zlim = zlim,
            label = "z[km]") 

set_title("Particle trajectory")
     
bpy.context.scene.cycles.tile_size = 256
bpy.context.scene.cycles.samples = 200

