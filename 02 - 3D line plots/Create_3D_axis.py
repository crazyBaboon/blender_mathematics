import bpy
import math

def create_diffuse_material(mesh, colour, name):
    material = bpy.data.materials.new(name = name)
    material.diffuse_color = colour
    mesh.data.materials.append(material)

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

def create_axis(axis, colour, thickness, set_grid):
    bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=2)
    bpy.ops.transform.resize(value=(thickness, thickness, thickness))

    if (axis == 'X'):
        bpy.ops.transform.rotate(value=math.radians(90), orient_axis='Y')
        bpy.ops.transform.resize(value=(1/thickness, 1, 1))
        bpy.ops.transform.translate(value=(1, 0, 0))
        # Set the X-axis to red
        axis_cilinder = bpy.context.active_object
        create_diffuse_material(axis_cilinder, colour, "axis_material")  
        #Add axis arrow
        bpy.ops.mesh.primitive_cone_add(radius1=1, radius2=0, depth=2)
        bpy.ops.transform.rotate(value=-math.radians(90), orient_axis='Y')
        bpy.ops.transform.translate(value=(2, 0, 0))
        bpy.ops.transform.resize(value=(3*thickness, 3*thickness, 3*thickness))
        # Set the cone to red
        cone = bpy.context.active_object
        create_diffuse_material(cone, colour, "cone_material")    
        #Add the auxaliary grid lines and corresponding planes:
        if set_grid == True:
            for N in range(1,4): # add the lines
                bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
                bpy.ops.transform.rotate(value=math.radians(90), orient_axis=axis)
                bpy.ops.transform.resize(value=(0.5*thickness, 0.5*thickness, 2))
                bpy.ops.transform.translate(value=(0.5*N, 0, 1))
                line = bpy.context.active_object
                create_diffuse_material(line, (0.1, 0.1, 0.1, 1), "line_material")
                               
            for N in range(1,4):
                bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
                bpy.ops.transform.resize(value=(0.5*thickness, 2, 1))                
                bpy.ops.transform.translate(value=(0.5*N, 1, 0)) 
                line = bpy.context.active_object
                create_diffuse_material(line, (0.1, 0.1, 0.1, 1), "line_material")
            
            # Add the planes
            bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
            bpy.ops.transform.resize(value=(2, 2, 1))                
            bpy.ops.transform.translate(value=(1, 1, -0.01))
            plane = bpy.context.active_object
            create_diffuse_material(plane, (0.973, 0.973, 0.973, 1), "plane_material")
                            
    elif (axis == 'Y'):  
        bpy.ops.transform.rotate(value=math.radians(90), orient_axis='X')
        bpy.ops.transform.resize(value=(1, 1/thickness, 1))
        bpy.ops.transform.translate(value=(0, 1, 0))
        # Set the X-axis to red
        axis_cilinder = bpy.context.active_object
        create_diffuse_material(axis_cilinder, colour, "axis_material")         
        #Add axis arrow
        bpy.ops.mesh.primitive_cone_add(radius1=1, radius2=0, depth=2)
        bpy.ops.transform.rotate(value=math.radians(90), orient_axis='X')
        bpy.ops.transform.translate(value=(0, 2, 0))
        bpy.ops.transform.resize(value=(3*thickness, 3*thickness, 3*thickness))
        # Set the cone to red
        cone = bpy.context.active_object
        create_diffuse_material(cone, colour, "cone_material")   
        #Add the auxaliary grid lines and corresponding planes:
        if set_grid == True:
            for N in range(1,4): # Add the lines
                bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
                bpy.ops.transform.rotate(value=math.radians(90), orient_axis=axis)
                bpy.ops.transform.resize(value=(0.5*thickness, 0.5*thickness, 2))
                bpy.ops.transform.translate(value=(0, 0.5*N, 1))
                line = bpy.context.active_object
                create_diffuse_material(line, (0.1, 0.1, 0.1, 1), "line_material")
                
            for N in range(1,4): 
                bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
                bpy.ops.transform.resize(value=(2, 0.5*thickness, 1))                
                bpy.ops.transform.translate(value=(1, 0.5*N, 0)) 
                line = bpy.context.active_object
                create_diffuse_material(line, (0.1, 0.1, 0.1, 1), "line_material")
            # Add the planes
            bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
            bpy.ops.transform.resize(value=(2, 2, 1))  
            bpy.ops.transform.rotate(value=math.radians(90), orient_axis=axis)              
            bpy.ops.transform.translate(value=(-0.01, 1, 1))
            plane = bpy.context.active_object
            create_diffuse_material(plane, (0.961, 0.961, 0.961, 1), "plane_material")   
                 
    elif (axis == 'Z'):    
        bpy.ops.transform.rotate(value=math.radians(90), orient_axis='Z')
        bpy.ops.transform.resize(value=(1, 1, 1/thickness))
        bpy.ops.transform.translate(value=(0, 0, 1))
        # Set the X-axis to red
        axis_cilinder = bpy.context.active_object
        create_diffuse_material(axis_cilinder, colour, "axis_material")         
        #Add axis arrow
        bpy.ops.mesh.primitive_cone_add(radius1=1, radius2=0, depth=2)
        bpy.ops.transform.rotate(value=math.radians(90), orient_axis=axis)
        bpy.ops.transform.translate(value=(0, 0, 2))
        bpy.ops.transform.resize(value=(3*thickness, 3*thickness, 3*thickness))
        # Set the cone to red
        cone = bpy.context.active_object
        create_diffuse_material(cone, colour, "cone_material")
        #Add the auxaliary grid lines and corresponding planes:
        if set_grid == True:
            for N in range(1,4): #add the lines
                bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
                bpy.ops.transform.resize(value=(2, 0.5*thickness, 1))
                bpy.ops.transform.translate(value=(1, 0, 0.5*N)) 
                line = bpy.context.active_object
                create_diffuse_material(line, (0.1, 0.1, 0.1, 1), "line_material") 
                
            for N in range(1,4): 
                bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
                bpy.ops.transform.resize(value=(0.5*thickness, 2, 1))                
                bpy.ops.transform.translate(value=(0, 1, 0.5*N))  
                line = bpy.context.active_object
                create_diffuse_material(line, (0.1, 0.1, 0.1, 1), "line_material")                            
            
            #add the planes
            bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
            bpy.ops.transform.resize(value=(2, 2, 1))  
            bpy.ops.transform.rotate(value=math.radians(90), orient_axis='X')              
            bpy.ops.transform.translate(value=(1, -0.01, 1))
            plane = bpy.context.active_object
            create_diffuse_material(plane, (0.949, 0.949, 0.949, 1), "plane_material")   


# Set ambient light colour
bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = (0.80, 0.80, 0.80, 1)

# set the camera position and direction
camera = bpy.data.objects.get("Camera")
camera.rotation_euler = (1.1938, 0, 2.1258)
camera.location.x = 6.9463
camera.location.y = 4.8738
camera.location.z = 3.6253

set_white_background()

#  create_axis( axis, RGBA, thickness, set_grid)
create_axis('X', (0.8, 0.1, 0.1, 1), 0.01, True) # red
create_axis('Y', (0.1, 0.8, 0.1, 1), 0.01, True) # green
create_axis('Z', (0.1, 0.1, 0.8, 1), 0.01, True) # blue

bpy.context.scene.cycles.tile_size = 256
bpy.context.scene.cycles.samples = 200




