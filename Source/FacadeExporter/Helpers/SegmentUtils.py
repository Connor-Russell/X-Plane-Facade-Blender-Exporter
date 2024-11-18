#Project: BlenderFacadeExporter
#Author: Connor Russell
#Date: 11/9/2024
#Purpose: Provide utility functions to help in extracting the geometry and attached objects from the individual objects in a layer.

#Blender modules
import collections
import math
import mathutils
import bpy
import bmesh

#Our modules
from . import GeometryUtils
from . import MiscUtils

#Simple container to hold attached object data  
class AttachedObj:
    #Class variables
    all_objects = []

    #Define instance varialbes
    def __init__(self):
        self.loc_x = 0
        self.loc_y = 0
        self.loc_z = 0

        self.rot_x = 0
        self.rot_y = 0
        self.rot_z = 0

        self.draped = False  #This defaults to graded. If true, the object is draped.

        self.resource = ""  #The path to the object

        self.min_draw = 0
        self.max_draw = 0

        self.valid = False

        self.roof_obj = False

    #Reads the data from an object
    def read_from_obj(self, obj):
        #Check to make sure this is an empty
        if obj.type != "EMPTY":
            return

        #Check if this object is exportable
        if not obj.facade_object.exportable:
            return
            
        #If the object has the 'FacadeObj' Property, get the value, otherwise return None
        if obj.facade_object.resource == "":
            return
        self.resource = obj.facade_object.resource

        #Get the draped
        self.draped = obj.facade_object.draped

        # Get the object's location and rotation
        self.loc_x = obj.location.x
        self.loc_y = obj.location.y
        self.loc_z = obj.location.z

        self.rot_x = obj.rotation_euler.x
        self.rot_y = obj.rotation_euler.y
        self.rot_z = obj.rotation_euler.z

        #Check if there is a parent. If so, we'll get it's transforms and apply that to the loc/rot
        if obj.parent != None:
            parent_transform = obj.parent.matrix_world

            # Get the local position as a vector
            local_position = mathutils.Vector((self.loc_x, self.loc_y, self.loc_z))

            # Apply the full transformation
            transformed_position = parent_transform @ local_position

            # Extract the rotation as Euler angles
            rotation = parent_transform.to_euler()

            # Set the new position and rotation
            self.loc_x = transformed_position.x
            self.loc_y = transformed_position.y
            self.loc_z = transformed_position.z

            self.rot_x = rotation.x
            self.rot_y = rotation.y
            self.rot_z = rotation.z

        #Convert the rotation to degrees
        self.rot_x = math.degrees(self.rot_x)
        self.rot_y = math.degrees(self.rot_y)
        self.rot_z = math.degrees(self.rot_z)

        self.valid = True
    
    #Resets the all objects list
    def reset_objects():
        AttachedObj.all_objects = []

    #Sorts and deduplicates the all objects list
    def prep_object_list():
        AttachedObj.all_objects.sort()

        #Iterate through the list (except for the last item) adn remove duplicates
        i = 0
        while i < len(AttachedObj.all_objects) - 1:
            if AttachedObj.all_objects[i] == AttachedObj.all_objects[i + 1]:
                AttachedObj.all_objects.pop(i)
            else:
                i += 1

    #Adds an object to the list of all objects so we can get it's index later
    def add_object_to_list(obj):
        #Make sure this is an empty
        if obj.type != "EMPTY":
            return
        
        #Check if it is exportable
        if not obj.facade_object.exportable:
            return
        
        #Check if it has the obj resource
        if obj.facade_object.resource == "":
            return
        
        #Get and store the resource
        resource = obj.facade_object.resource
        AttachedObj.all_objects.append(resource)
        

    #Get the string representation of this object
    def get_string(self):
        out = ""
        if self.roof_obj:
            out += "ROOF_OBJ_HEADING "
        elif self.draped:
            out += "ATTACH_DRAPED "
        else:
            out += "ATTACH_GRADED "

        #Get the index of this object's resource in the list of all objects
        try:
            index = MiscUtils.linear_search_list(AttachedObj.all_objects, self.resource)
        except ValueError:
            print("Error: Resource not found in list of all objects. Number of object in list:" + str(len(AttachedObj.all_objects)))
            index = 0

        #Add the data index, x, y, z, rot_z, min_draw, max_draw
        if self.roof_obj:
            out += str(index) + " " + MiscUtils.ftos(self.loc_x, 8) + " " + MiscUtils.ftos(self.loc_y, 8) + " " + MiscUtils.ftos(MiscUtils.resolve_heading(self.rot_z * -1), 4) + " " + str(self.min_draw) + " " + str(self.max_draw)
        else:
            out += str(index) + " " + MiscUtils.ftos(self.loc_x, 8) + " " + MiscUtils.ftos(self.loc_z, 8) + " " + MiscUtils.ftos(self.loc_y, 8) + " " + MiscUtils.ftos(MiscUtils.resolve_heading(self.rot_z + 180), 3) + " " + str(self.min_draw) + " " + str(self.max_draw)

        return out

#Get the geometry from an object. Returns a tuple of XPVertex and integer indicies that represent the faces.
def get_geometry_from_obj(obj):
    # Ensure the object is a mesh
    if obj.type != 'MESH':
        raise TypeError("Object must be a mesh")

    #Get our mesh data
    mesh = obj.data

    #Calculate split normals if this mesh has them
    if hasattr(mesh, "calc_normals_split"):
        mesh.calc_normals_split()

    #Triangulate the mesh and get the loop triangles
    mesh.calc_loop_triangles()
    loop_triangles = mesh.loop_triangles

    #Attempt to get the uv layer. We look for the first layer. 
    try:
        uv_layer = mesh.uv_layers[0]
    except (KeyError, TypeError) as e:
        uv_layer = None

    #Define a temporary data structure to hold our triangle faces.
    XPTriangle = collections.namedtuple(
                    "XPTriangle",
                    field_names=[
                        "vertex_pos",  # Tuple[Tuple[float, float, float], Tuple[float, float, float], Tuple[float, float, float]] Tuple containing the positions for each vertex. Only used when smooth is true
                        "vertex_nrm",  # Tuple[Tuple[float, float, float], Tuple[float, float, float], Tuple[float, float, float]] Tuple containing the normals for each vertex. Only used when smooth is true
                        "uvs",  # type: Tuple[[float, float], [float, float], [float, float]]
                    ],
                )
    
    #Define an array to hold our faces
    xp_triangles = []

    #Now we iterate through teh loop triangles to populate our array of XPTriangles
    for tri in loop_triangles:

        #Define our UV and normal data beforehand. The struct is immutable so we can't change it after the fact
        xp_triangle_uvs = ((0, 0), (0, 0), (0, 0))
        if uv_layer != None:
            xp_triangle_uvs = (uv_layer.data[tri.loops[0]].uv, uv_layer.data[tri.loops[1]].uv, uv_layer.data[tri.loops[2]].uv)

        xp_triangles_normals = (tri.split_normals[0], tri.split_normals[1], tri.split_normals[2])
        if not tri.use_smooth:
            xp_triangles_normals = (tri.normal, tri.normal, tri.normal)


        #Define a temporary face with the data from the loop triangle. UVs default to none so we can add them IF we do have a uv layer
        tmp_face = XPTriangle(
            vertex_pos = (mesh.vertices[tri.vertices[0]].co, mesh.vertices[tri.vertices[1]].co, mesh.vertices[tri.vertices[2]].co),
            vertex_nrm = xp_triangles_normals,
            uvs = xp_triangle_uvs
        )

        #Append the face to the array
        xp_triangles.append(tmp_face)

    #Now that we have the faces stored, we need to actually turn them into verticies and indicies.
    #This is a bit more complicated. We have to iterate through every face. Then we need to check if *any* of it's 3 verticies already exist - if they do, we will use the existing one instead
    #Once we know the indicies of each vertex because it's either been added, or already exists, we can do the index output array, which would be in the order of last vertex, middle, first. 

    #Define our output arrays
    out_verts = []  #Array of XPVertex
    out_inds = []   #Ints

    for t in xp_triangles:
        #Define verticies for each triangle. Then see if they exist, if they don't, add them.
        v1 = GeometryUtils.XPVertex(t.vertex_pos[0][0], t.vertex_pos[0][1], t.vertex_pos[0][2], t.vertex_nrm[0][0], t.vertex_nrm[0][1], t.vertex_nrm[0][2], t.uvs[0][0], t.uvs[0][1])
        v2 = GeometryUtils.XPVertex(t.vertex_pos[1][0], t.vertex_pos[1][1], t.vertex_pos[1][2], t.vertex_nrm[1][0], t.vertex_nrm[1][1], t.vertex_nrm[1][2], t.uvs[1][0], t.uvs[1][1])
        v3 = GeometryUtils.XPVertex(t.vertex_pos[2][0], t.vertex_pos[2][1], t.vertex_pos[2][2], t.vertex_nrm[2][0], t.vertex_nrm[2][1], t.vertex_nrm[2][2], t.uvs[2][0], t.uvs[2][1])

        try_optomize = False

        if try_optomize:
            v1_index = MiscUtils.linear_search_list(out_verts, v1)
            v2_index = MiscUtils.linear_search_list(out_verts, v2)
            v3_index = MiscUtils.linear_search_list(out_verts, v3)

            if v1_index == -1:
                out_verts.append(v3)
                v1_index = len(out_verts) - 1
            if v2_index == -1:
                out_verts.append(v2)
                v2_index = len(out_verts) - 1
            if v3_index == -1:
                out_verts.append(v1)
                v3_index = len(out_verts) - 1
        else:
            out_verts.append(v3)
            v1_index = len(out_verts) - 1
            out_verts.append(v2)
            v2_index = len(out_verts) - 1
            out_verts.append(v1)
            v3_index = len(out_verts) - 1

        #Now finally we add the indicies! These are in the order v3, v2, v1
        out_inds.append(v3_index)
        out_inds.append(v2_index)
        out_inds.append(v1_index)

    #Now we need to get the transform matrix for the object
    transform = obj.matrix_world

    #Now we loop through the verticies and apply the transform to each one
    for v in out_verts:
        #Get the local position as a vector
        local_position = mathutils.Vector((v.loc_x, v.loc_y, v.loc_z))
        normal = mathutils.Vector((v.normal_x, v.normal_y, v.normal_z))

        #Apply the full transformation
        transformed_position = transform @ local_position

        #Work to apply the transform to the normals
        normal_matrix = obj.matrix_world.inverted().transposed()
        transformed_normal = normal_matrix @ normal
        transformed_normal.normalize()

        #Set the new position and rotation
        v.loc_x = transformed_position.x
        v.loc_y = transformed_position.y
        v.loc_z = transformed_position.z

        #Set the new normal
        v.normal_x = transformed_normal.x
        v.normal_y = transformed_normal.y
        v.normal_z = transformed_normal.z

    #Return the verticies and indicies
    return (out_verts, out_inds)
