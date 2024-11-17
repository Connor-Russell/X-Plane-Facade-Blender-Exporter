#Project: BlenderFacadeExporter
#Author: Connor Russell
#Date: 11/14/2024
#Purpose: Provide a single function call to get the facade file text from all the collections

import bpy
from .Helpers import SegmentUtils
from . import GetSegment
from . import GetRoof

def get_collections_in_ui_order():
    collections = []
    for col in bpy.context.view_layer.layer_collection.children:
        if collections is None:
            collections = []
        if col.exclude:
            continue
        collections.append(col.collection)
    
    return collections

def get_facade():
    #Get the collections
    collections = get_collections_in_ui_order()

    #Define a list of collections that are exportable
    exportable_segments = []
    exportable_curved_segments = []
    roof_collection = None

    #Iterate through every collection
    for col in collections:
        #Get the name of the collection
        col_name = col.name

        #Make the name lowercase
        col_name = col_name.lower()

        #Make sure this facade name doesn't end in _curved
        if col_name.endswith("_curved"):
            continue

        if col_name == "roof":
            roof_collection = col
            continue

        #Append this collection to the exportable list
        exportable_segments.append(col)

        #Check all the other collections for a name_curved variant
        did_find_curved = False
        for curved_col in collections:
            curved_col_name = curved_col.name
            curved_col_name = curved_col_name.lower()
            if curved_col_name == col_name + "_curved":
                exportable_curved_segments.append(curved_col)
                did_find_curved = True
                break
        
        #If we didn't find a curved variant, append None, we'll use the text from the straight segment
        if not did_find_curved:
            exportable_curved_segments.append(None)

    #We now have a list of exportable segments, exportable curved segments, and the roof collection.
    #So now, we need to:
    #1. Get a list of all facade objects
    #2. Load the facade roof (since it goes into the header)
    #3. Get the facade header text
    #4. Get the roof text
    #5. Get the facade segment text, and corresponding curved text
    #6. Get the spelling text
    #7. Merge it all together and return it

    #Shortcut for the facade properties
    f = bpy.context.scene.facade_exporter

    #1. Get a list of all facade objects
    for col in exportable_segments:
        if col == None:
            continue
        for obj in col.objects:
            if obj == None:
                continue
            SegmentUtils.AttachedObj.add_object_to_list(obj)
    for col in exportable_curved_segments:
        if col == None:
            continue
        for obj in col.objects:
            if obj == None:
                continue
            SegmentUtils.AttachedObj.add_object_to_list(obj)
    if roof_collection != None:
        for obj in roof_collection.objects:
            if obj == None:
                continue
            SegmentUtils.AttachedObj.add_object_to_list(obj)

    SegmentUtils.AttachedObj.prep_object_list()

    #2. Load the facade roof
    roof = GetRoof.FacadeRoof()
    if roof_collection != None: #If there is a roof collection, load it, otherwise just default the roof to 10x10. If they don't have a roof they probably don't care
        roof.read_from_collection(roof_collection)
    else:
        roof.roof_scale_x = 10
        roof.roof_scale_y = 10

    #3. Get the facade header text
    header_text = "I\n1000\nFACADE\n\n"

    #General properties
    if f.ring:
        header_text += "RING 1\n"
    else:
        header_text += "RING 0\n"
    if f.graded:
        header_text += "GRADED\n"
    else:
        header_text += "DRAPED\n"
    if f.layergroup != "":
        header_text += "LAYER_GROUP " + f.layergroup + "\n"
    if f.layergroup_draped != "":
        header_text += "LAYER_GROUP_DRAPED " + f.layergroup_draped + "\n"

    #Wall properties
    if f.render_wall:
        #Specify this is for the wall shader, if we have anything to do
        if f.wall_texture_alb != "" or f.wall_texture_nml != "":
            header_text += "\nSHADER_WALL\n"

        if f.wall_texture_alb != "":
            header_text += "TEXTURE " + f.wall_texture_alb + "\n"
        if f.wall_texture_nml != "":
            header_text += "TEXTURE_NORMAL " + str(f.wall_texture_nml_scale) + " " + f.wall_texture_nml + "\n"
    else:
        header_text += "\nNO_WALL_MESH\n"

    #Roof properties
    if f.render_roof:
        #Specify this is for the roof shader, if we have anything to dos
        if f.roof_texture_alb != "" or f.roof_texture_nml != "":
            header_text += "\nSHADER_ROOF\n"

        if f.roof_texture_alb != "":
            header_text += "TEXTURE " + f.roof_texture_alb + "\n"
        if f.roof_texture_nml != "":
            header_text += "TEXTURE_NORMAL " + str(f.roof_texture_nml_scale) + " " + f.roof_texture_nml + "\n"     
    else:
        header_text += "\nNO_ROOF_MESH\n"

    #Object definitions
    for obj in SegmentUtils.AttachedObj.all_objects:
        header_text += "OBJ " + obj + "\n"

    #4. Get the roof text
    roof_text = ""
    roof_text += "FLOOR Default\n"
    roof_text += "ROOF_HEIGHT " + str(f.roof_height) + "\n"
    roof_text += "ROOF_SCALE " + str(roof.roof_scale_x) + " " + str(roof.roof_scale_y) + "\n"

    if len(roof.roof_objs) > 0:
        roof_text += "\n"

    for obj in roof.roof_objs:
        obj.roof_obj = True
        roof_text += obj.get_string() + "\n"

    #5. Get the facade curve and straight segment text
    straight_segment_text = []
    curved_segment_text = []

    #Straight
    for i in range(0, len(exportable_segments)):
        straight_segment_text.append(GetSegment.get_segment(exportable_segments[i]))

    #Curved
    for i in range(0, len(exportable_curved_segments)):
        if exportable_curved_segments[i] == None:
            curved_segment_text.append(straight_segment_text[i])
        else:
            curved_segment_text.append(GetSegment.get_segment(exportable_curved_segments[i]))

    #6. Get the spelling text.
    spelling_text = "" 
    for index, item in enumerate(f.spellings):
        if item.type == "WALL":
            spelling_text += "WALL " + str(item.min_width) + " " + str(item.max_width) + " " + str(item.min_heading) + " " + str(item.max_heading) + " " + item.wall_name + "\n"
        elif item.type == "WALL_RULE":
            spelling_text += "WALL_RULE " + str(item.min_width) + " " + str(item.max_width) + " " + str(item.min_heading) + " " + str(item.max_heading) + "\n"
        else:
            spelling_text += "SPELLING " + str(item.spellings) + "\n"

    #7. Merge it all together and return it
    facade_text = header_text + "\n" + roof_text + "\n"

    for i in range(0, len(straight_segment_text)):
        facade_text += "SEGMENT " + str(i) + "\n" + straight_segment_text[i] + "\n"
    
    for i in range(0, len(curved_segment_text)):
        facade_text += "SEGMENT_CURVED " + str(i) + "\n" + curved_segment_text[i] + "\n"

    facade_text += spelling_text

    return facade_text



