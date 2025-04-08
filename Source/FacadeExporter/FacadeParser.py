
import os
import bpy  # type: ignore
from bpy_extras.io_utils import ImportHelper # type: ignore

from .Helpers.GeometryUtils import create_mesh_from_draw_call
from .Helpers.GeometryUtils import XPVertex
from .Helpers.SegmentUtils import AttachedObj

def import_facade(inPfac_file_path):

    current_group = 0
    current_far_lod = 0
    current_cuts = 0
    object_defs = []
    current_verts = []
    current_indices = []
    current_idx = -1    #-1 is roof, otherwise idx of the segment
    is_first_curved_segment = True
    is_first_floor = True

    roof_scale_x = 0.0
    roof_scale_y = 0.0
    roof_objects = []
    roof_height = 0.0

    do_have_roof_mesh = True

    #Open the file and read line by line
    with open(inPfac_file_path, 'r') as pfac_file:
        lines = pfac_file.readlines()

        #Iterate over lines
        for line in lines:
            #Split the line into parts
            parts = line.split()

            if len(parts) == 0:
                continue

            #Check the command
            if parts[0] == 'NO_ROOF_MESH':
                do_have_roof_mesh = False
            elif parts[0] == 'OBJ':
                #Format: OBJ <resource>
                #This just defines an object referenceable by an index
                new_obj_resource = parts[1]
                object_defs.append(new_obj_resource)
            elif parts[0] == 'FLOOR':
                if not is_first_floor:
                    break
                is_first_floor = False
            elif parts[0] == 'ROOF_SCALE':
                #Format: ROOF_SCALE <scale_x> <scale_y>(optional)
                roof_scale_x = float(parts[1])
                if len(parts) > 2:
                    roof_scale_y = float(parts[2])
                else:
                    roof_scale_y = roof_scale_x
            elif parts[0] == 'ROOF_HEIGHT':
                #Format: ROOF_HEIGHT <height>
                roof_height = float(parts[1])
            elif parts[0] == 'ROOF_OBJ' or parts[0] == 'ROOF_OBJ_HEADING':
                #Format: ROOF_OBJ <index> <s> <t> <rotation>(optional) <lo> <hi>
                new_obj = AttachedObj()
                new_obj.resource = object_defs[int(parts[1])]
                new_obj.loc_x = float(parts[2])
                new_obj.loc_y = float(parts[3])
                if len(parts) == 8 or len(parts) == 9:
                    new_obj.rot_z = float(parts[4])

                roof_objects.append(new_obj)
            elif parts[0] == 'VERTEX':
                #We swap Z and Y because of XP coventions
                cur_vert = XPVertex(0, 0, 0, 0, 0, 0, 0, 0)
                cur_vert.loc_x = float(parts[1])
                cur_vert.loc_z= float(parts[2])
                cur_vert.loc_y = float(parts[3])
                cur_vert.normal_x = float(parts[4])
                cur_vert.normal_z = float(parts[5])
                cur_vert.normal_y = float(parts[6])
                cur_vert.uv_x = float(parts[7])
                cur_vert.uv_y = float(parts[8])

                current_verts.append(cur_vert)
            elif parts[0] == 'IDX':
                #Iterate through the indicies list and add them to the current indicies list
                for i in range(1, len(parts)):
                    current_indices.append(int(parts[i]))
            elif parts[0] == 'ATTACH_GRADED' or parts[0] == 'ATTACH_DRAPED':
                #Create a new empty object and set the properties
                new_empty = bpy.data.objects.new("Attached Object", None)
                new_empty.empty_display_type = 'ARROWS'
                new_empty.empty_display_size = 1
                new_empty.facade_object.draped = (parts[0] == 'ATTACH_DRAPED')
                new_empty.facade_object.resource = object_defs[int(parts[1])]
                new_empty.facade_object.exportable = True
                new_empty.facade_object.group = 0
                new_empty.location = (new_obj.loc_x, new_obj.loc_y, new_obj.loc_z)
                new_empty.rotation_euler = (0, 0, new_obj.rot_z)

                #Link to the current collection
                bpy.context.collection.objects.link(new_empty)
            elif parts[0] == 'MESH':
                #Create the *last* mesh object
                if len(current_verts) > 0:
                    new_obj = create_mesh_from_draw_call(current_verts, current_indices, "Segment")
                    new_obj.facade_object.group = current_group
                    new_obj.facade_object.far_lod = current_far_lod
                    new_obj.facade_object.cuts = current_cuts
                    new_obj.facade_object.exportable = True

                    current_verts = []
                    current_indices = []

                current_group = int(float(parts[1]))
                current_far_lod = int(float(parts[2]))
                current_cuts = int(float(parts[3]))
            elif parts[0] == 'SEGMENT' or parts[0] == 'SEGMENT_CURVED':
                if current_idx == -1 and do_have_roof_mesh:
                    #Create a new collection
                    new_collection = bpy.data.collections.new("ROOF")
                    bpy.context.scene.collection.children.link(new_collection)
                    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[new_collection.name]

                    #Create the verticies for the roof obj
                    bottom_left = XPVertex(0, 0, 0, 0, 0, 0, 0, 0)
                    bottom_right = XPVertex(0, 0, 0, 0, 0, 0, 0, 0)
                    top_left = XPVertex(0, 0, 0, 0, 0, 0, 0, 0)
                    top_right = XPVertex(0, 0, 0, 0, 0, 0, 0, 0)
                    bottom_left.loc_x = 0
                    bottom_left.loc_y = 0
                    bottom_left.normal_x = 0
                    bottom_left.normal_y = 0
                    bottom_left.normal_z = 1
                    bottom_left.uv_x = 0
                    bottom_left.uv_y = 0

                    bottom_right.loc_x = roof_scale_x
                    bottom_right.loc_y = 0
                    bottom_right.normal_x = 0
                    bottom_right.normal_y = 0
                    bottom_right.normal_z = 1
                    bottom_right.uv_x = 1
                    bottom_right.uv_y = 0

                    top_left.loc_x = 0
                    top_left.loc_y = roof_scale_y
                    top_left.normal_x = 0
                    top_left.normal_y = 0
                    top_left.normal_z = 1
                    top_left.uv_x = 0
                    top_left.uv_y = 1

                    top_right.loc_x = roof_scale_x
                    top_right.loc_y = roof_scale_y
                    top_right.normal_x = 0
                    top_right.normal_y = 0
                    top_right.normal_z = 1
                    top_right.uv_x = 1
                    top_right.uv_y = 1

                    roof_obj = create_mesh_from_draw_call([bottom_left, bottom_right, top_left, top_right], [0, 1, 2, 1, 3, 2], "Roof")
                    roof_obj.location = (0, 0, roof_height)

                    #Iterate over the roof objects and add them to the roof object
                    for roof_obj_data in roof_objects:
                        new_empty = bpy.data.objects.new("Attached Object", None)
                        new_empty.empty_display_type = 'ARROWS'
                        new_empty.empty_display_size = 1
                        new_empty.facade_object.draped = False
                        new_empty.facade_object.resource = roof_obj_data.resource
                        new_empty.facade_object.exportable = True
                        new_empty.facade_object.group = 0
                        new_empty.location = (roof_obj_data.loc_x, roof_obj_data.loc_y, roof_height + roof_obj_data.loc_z)
                        new_empty.rotation_euler = (0, 0, roof_obj_data.rot_z)

                        #Link to the current collection
                        bpy.context.collection.objects.link(new_empty)

                #Create the *last* mesh object
                elif len(current_verts) > 0:
                    new_obj = create_mesh_from_draw_call(current_verts, current_indices, "Segment")
                    new_obj.facade_object.group = current_group
                    new_obj.facade_object.far_lod = current_far_lod
                    new_obj.facade_object.cuts = current_cuts
                    new_obj.facade_object.exportable = True

                    current_verts = []
                    current_indices = []

                #Create a new collection and make it the active collection
                new_collection = bpy.data.collections.new(parts[1])
                bpy.context.scene.collection.children.link(new_collection)
                bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[new_collection.name]

                #Reset index if this is the first curved segment
                current_idx += 1
                if is_first_curved_segment and parts[0] == 'SEGMENT_CURVED':
                    current_idx = 0
                    is_first_curved_segment = False

                #Name it the WALL_<current_idx>[_curved](if this is a curved segment)
                new_collection.name = "WALL_" + str(current_idx) + ("_curved" if parts[0] == 'SEGMENT_CURVED' else "")

    #Append the last mesh object
    if len(current_verts) > 0:
        new_obj = create_mesh_from_draw_call(current_verts, current_indices, "Segment")
        new_obj.facade_object.group = current_group
        new_obj.facade_object.far_lod = current_far_lod
        new_obj.facade_object.cuts = current_cuts
        new_obj.facade_object.exportable = True

        current_verts = []
        current_indices = []

class IMPORT_xp_fac(bpy.types.Operator, ImportHelper):
    bl_idname = "import_scene.xp_fac"
    bl_label = "Import X-Plane Facades"
    filename_ext = ".fac"
    filter_glob: bpy.props.StringProperty(default="*.fac", options={'HIDDEN'}) # type: ignore
    files: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)  # To support multiple files

    def execute(self, context):
        # Implement your import logic here
        directory = self.filepath
        directory = directory[:directory.rfind("\\")]

        for cf in self.files:
            filepath = f"{directory}\\{cf.name}"
            import_facade(filepath)

        return {'FINISHED'}

            
