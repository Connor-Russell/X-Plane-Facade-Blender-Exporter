#Project: BlenderFacadeExporter
#Author: Connor Russell
#Date: 11/9/2024
#Purpose: Provide utility functions to work with geometry (things like rotating a point, etc)

import math
import bpy
import bmesh
from . import MiscUtils

#Simple container to hold an X-Plane Vertex
class XPVertex:
    loc_x = 0
    loc_y = 0
    loc_z = 0

    normal_x = 0
    normal_y = 0
    normal_z = 0

    uv_x = 0
    uv_y = 0

    def __init__(self, loc_x, loc_y, loc_z, normal_x, normal_y, normal_z, uv_x, uv_y):
        self.loc_x = loc_x
        self.loc_y = loc_y
        self.loc_z = loc_z

        self.normal_x = normal_x
        self.normal_y = normal_y
        self.normal_z = normal_z

        self.uv_x = uv_x
        self.uv_y = uv_y

    def __eq__(self, other):
        return self.loc_x == other.loc_x and self.loc_y == other.loc_y and self.loc_z == other.loc_z and self.normal_x == other.normal_x and self.normal_y == other.normal_y and self.normal_z == other.normal_z and self.uv_x == other.uv_x and self.uv_y == other.uv_y

    def to_string(self):
        return "VERTEX\t" + MiscUtils.ftos(self.loc_x, 8) + "\t" + MiscUtils.ftos(self.loc_z, 8) + "\t" + MiscUtils.ftos(self.loc_y, 8) + "\t" + MiscUtils.ftos(self.normal_x, 8) + "\t" + MiscUtils.ftos(self.normal_z, 8) + "\t" + MiscUtils.ftos(self.normal_y, 8) + "\t" + MiscUtils.ftos(self.uv_x, 8) + "\t" + MiscUtils.ftos(self.uv_y, 8)

#Rotate a vertex around an axis ("x", "y", or "z"). Angle must be in degrees. Returns the new vertex as a tuple of x y z in that order.
def rotate_vertex_on_axis(vertex, angle, axis):
    # Convert the angle to radians
    angle = math.radians(angle)

    # Get the sin and cos of the angle
    sin = math.sin(angle)
    cos = math.cos(angle)

    # Get the axis
    axis = axis.lower()

    # Rotate the vertex
    if axis == "x":
        new_x = vertex[0]
        new_y = vertex[1] * cos - vertex[2] * sin
        new_z = vertex[1] * sin + vertex[2] * cos
    elif axis == "y":
        new_x = vertex[0] * cos + vertex[2] * sin
        new_y = vertex[1]
        new_z = -vertex[0] * sin + vertex[2] * cos
    elif axis == "z":
        new_x = vertex[0] * cos - vertex[1] * sin
        new_y = vertex[0] * sin + vertex[1] * cos
        new_z = vertex[2]
    else:
        raise ValueError("Invalid axis. Must be 'x', 'y', or 'z'")

    return (new_x, new_y, new_z)

#Creates an object in Blender with the specified verticies and indicies (from the X-Plane format)
def create_debug_obj(verticies, indicies):
    #Create a new bmesh
    bm = bmesh.new()

    #Iterate through the indicies, 3 at a time, and create a face with the verticies at specified indicies
    i = 0
    while i < len(indicies) - 2:
        # Add vertices to the bmesh
        v1 = verticies[indicies[i]]
        v2 = verticies[indicies[i + 1]]
        v3 = verticies[indicies[i + 2]]
        verts = [bm.verts.new((v1.loc_x, v1.loc_y, v1.loc_z)), bm.verts.new((v2.loc_x, v2.loc_y, v2.loc_z)), bm.verts.new((v3.loc_x, v3.loc_y, v3.loc_z))]

        # Update the bmesh to ensure the vertices are added
        bm.verts.ensure_lookup_table()

        # Create a new face with the vertices
        bm.faces.new(verts)

        # Update the bmesh to ensure the face is added
        bm.faces.ensure_lookup_table()

        i = i + 3

    # Finish up, write the bmesh back to the mesh
    mesh = bpy.data.meshes.new("Mesh")
    bm.to_mesh(mesh)
    bm.free()

    # Create an object with the mesh
    obj = bpy.data.objects.new("Debug", mesh)

    # Link the object to the root scene collection
    bpy.context.collection.objects.link(obj)

def create_mesh_from_draw_call(verticies, indicies, name):
    #Create a new bmesh
    bm = bmesh.new()

    #Add all the verticies
    for vertex in verticies:
        bm.verts.new((vertex.loc_x, vertex.loc_y, vertex.loc_z))

    # Update the bmesh to ensure the vertices are added
    bm.verts.ensure_lookup_table()

    #Create a uv layer
    uv_layer = bm.loops.layers.uv.new()

    #Iterate through the indicies, 3 at a time, and create a face with the verticies at specified indicies
    i = 0

    while i < len(indicies) - 2:
        # Add vertices to the bmesh
        v1 = verticies[indicies[i]]
        v2 = verticies[indicies[i + 1]]
        v3 = verticies[indicies[i + 2]]

        #Create new vertices in the bmesh for each vertex
        v1 = bm.verts.new((v1.loc_x, v1.loc_y, v1.loc_z))
        v2 = bm.verts.new((v2.loc_x, v2.loc_y, v2.loc_z))
        v3 = bm.verts.new((v3.loc_x, v3.loc_y, v3.loc_z))
        
        #Set the normals for the vertices
        v1.normal = (verticies[indicies[i]].normal_x, verticies[indicies[i]].normal_y, verticies[indicies[i]].normal_z)
        v2.normal = (verticies[indicies[i + 1]].normal_x, verticies[indicies[i + 1]].normal_y, verticies[indicies[i + 1]].normal_z)
        v3.normal = (verticies[indicies[i + 2]].normal_x, verticies[indicies[i + 2]].normal_y, verticies[indicies[i + 2]].normal_z)

        # Update the bmesh to ensure the vertices are added
        bm.verts.ensure_lookup_table()

        # Create a new face with the vertices
        face = bm.faces.new([v1, v2, v3])

        #Assign the UV coordinates to the face
        face.loops[0][uv_layer].uv = (verticies[indicies[i]].uv_x, verticies[indicies[i]].uv_y)
        face.loops[1][uv_layer].uv = (verticies[indicies[i + 1]].uv_x, verticies[indicies[i + 1]].uv_y)
        face.loops[2][uv_layer].uv = (verticies[indicies[i + 2]].uv_x, verticies[indicies[i + 2]].uv_y)

        # Update the bmesh to ensure the face is added
        bm.faces.ensure_lookup_table()

        i = i + 3

    # Finish up, write the bmesh back to the mesh
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()

    # Create an object with the mesh and link it to the scene
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj

    return obj
