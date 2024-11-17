#Project: BlenderFacadeExporter
#Author: Connor Russell
#Date: 11/9/2024
#Purpose: Provide a single function call to get the geometry of a segment, and attached objects, from a layer in a blender scene. 

#Our modules
from .Helpers import SegmentUtils
from .Helpers import MiscUtils
from .Helpers import GeometryUtils

#Gets the geometry of a segment, and attached objects, from a layer in a blender scene. Returns the all data in a string, formatted for an X-Plane Facade
def get_segment(layer):

    #Define an empty array of attached objects
    attached_objects = []

    #Define a string to hold output
    output = ""

    #Iterate through the objects in the layer
    for obj in layer.objects:
        #If the object is a segment, get its geometry
        if obj.type == "MESH":
            #Get the geometry of this object
            geometry = SegmentUtils.get_geometry_from_obj(obj)

            #add the mesh header (MESH <group> <far LOD> <cuts> <vertex_count> <idx_count>)
            output += "MESH\t" + str(obj.facade_object.group) + "\t" + str(obj.facade_object.far_lod) + "\t" + str(obj.facade_object.cuts) + "\t" + str(len(geometry[0])) + "\t" + str(len(geometry[1])) + "\n"

            #Add the verticies
            for v in geometry[0]:
                output += v.to_string() + "\n"

            #Add the indicies
            for i in range(0, len(geometry[1])):
                #Add the newline idx
                if (i + 1) % 10 == 1:
                    output += "IDX "

                #Add the index
                output += str(geometry[1][i]) + " "

                #Add the newline every 10 indicies
                if (i + 1) % 10 == 0 and i != 0:
                    output += "\n"
            output += "\n"

        #If this is an empty, these typically are an attached object. We will check and handle that here.
        if obj.type == "EMPTY":
            attached_obj = SegmentUtils.AttachedObj()
            attached_obj.read_from_obj(obj)

            if attached_obj.valid:
                attached_objects.append(attached_obj)

    #Add the attached objects
    for obj in attached_objects:
        output += obj.get_string() + "\n"

    #Return the output
    return output
