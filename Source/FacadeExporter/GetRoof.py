#Project: BlenderFacadeExporter
#Author: Connor Russell
#Date: 11/9/2024
#Purpose: Provides a class to abstract the roof definition for a facade

from .Helpers.SegmentUtils import AttachedObj

#Class containing the details of a roof
class FacadeRoof:

    def __init__(self):
        self.roof_scale_x = 1
        self.roof_scale_y = 1

        #These are AttachedObjs from Helpers.SegmentUtils
        self.roof_objs = []

    def read_from_collection(self, collection):
        #Loop through and find the first mesh object
        for obj in collection.objects:
            if obj.type == 'MESH':
                #Get this object's dimensions. This will be used to scale the roof
                self.roof_scale_x = obj.dimensions.x
                self.roof_scale_y = obj.dimensions.y

            elif obj.type == 'EMPTY':
                #Attempt to load this attached object and save it if the results are not None
                roof_obj = AttachedObj()
                roof_obj.read_from_obj(obj)

                if roof_obj.valid:
                    self.roof_objs.append(roof_obj)