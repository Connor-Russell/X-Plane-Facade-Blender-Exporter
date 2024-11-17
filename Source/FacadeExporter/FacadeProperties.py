#Project: BlenderFacadeExporter
#Author: Connor Russell
#Date: 11/14/2024
#Purpose: Contains the properties for the whole facade in Blender. There can only be one facade per file.

import bpy
import os

from . import GetFacade

#Forced a UI update
def update_ui(self, context):
    context.area.tag_redraw()

class FacadeSpellingItem(bpy.types.PropertyGroup):
    type: bpy.props.EnumProperty(
        name="Type",
        items=[
            ("WALL", "Wall", "Wall definition"),
            ("WALL_RULE ", "Wall Rule", "Second wall rule"),
            ("SPELLING", "Spelling", "Wall spelling")
        ],
        update=update_ui)
    min_width: bpy.props.FloatProperty(name="Min Width", description="The minimum width of the wall")
    max_width: bpy.props.FloatProperty(name="Max Width", description="The maximum width of the wall")
    min_heading: bpy.props.FloatProperty(name="Min Heading", description="The minimum heading of the wall")
    max_heading: bpy.props.FloatProperty(name="Max Heading", description="The maximum heading of the wall")
    spellings: bpy.props.StringProperty(name="Spellings", default="", update=update_ui)
    wall_name: bpy.props.StringProperty(name="Wall Name", default="", update=update_ui)

#Class containing the properties for the UI
class PROP_facade_exporter(bpy.types.PropertyGroup):

    #Facade name
    facade_name: bpy.props.StringProperty( name="Facade Name", description="The name of the facade")

    #Global properties
    graded: bpy.props.BoolProperty(name="Graded", description="Whether the facade is graded, otherwise draped")
    ring: bpy.props.BoolProperty(name="Ring", description="Whether the facade is a closed or an open ring")
    layergroup: bpy.props.StringProperty(name="Layer Group", description="The layer group of the facade")
    layergroup_draped: bpy.props.StringProperty(name="Layer Group Draped", description="The layer group of the draped facade")
    solid: bpy.props.BoolProperty(name="Solid", description="Whether the roof has collision testing enabled")

    #Wall properties
    render_wall: bpy.props.BoolProperty(name="Render Wall", description="Whether the wall is rendered", update=update_ui)
    wall_texture_alb: bpy.props.StringProperty(name="Texture ALB Path", description="The relative path of the ALB", subtype='FILE_PATH')
    wall_texture_nml: bpy.props.StringProperty(name="Texture NML Path", description="The relative path of the NML", subtype='FILE_PATH')
    wall_texture_nml_scale: bpy.props.FloatProperty(name="Texture NML Scale", description="The scale of the NML texture")

    #Roof properties
    render_roof: bpy.props.BoolProperty(name="Render Roof", description="Whether the roof is rendered", update=update_ui)
    roof_texture_alb: bpy.props.StringProperty(name="Texture ALB Path", description="The relative path of the ALB", subtype='FILE_PATH')
    roof_texture_nml: bpy.props.StringProperty(name="Texture NML Path", description="The relative path of the NML", subtype='FILE_PATH')
    roof_texture_nml_scale: bpy.props.FloatProperty(name="Texture NML Scale", description="The scale of the NML texture")
    roof_height: bpy.props.FloatProperty(name="Roof Height", description="The height of the roof")

    #Spellings
    spellings: bpy.props.CollectionProperty(type=FacadeSpellingItem)

class MENU_BT_facade_exporter_add_spelling(bpy.types.Operator):
    bl_idname = "object.add_spelling"
    bl_label = "Add Spelling"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.facade_exporter.spellings.add()
        return {'FINISHED'}

class MENU_BT_facade_exporter_remove_spelling(bpy.types.Operator):
    bl_idname = "object.remove_spelling"
    bl_label = "Remove Spelling"
    bl_options = {'REGISTER', 'UNDO'}

    index: bpy.props.IntProperty()

    def execute(self, context):
        context.scene.facade_exporter.spellings.remove(self.index)
        return {'FINISHED'}
    
#Class that creates the UI
class MENU_facade_exporter(bpy.types.Panel):
    """Creates a Panel in the scene properties window"""
    bl_label = "X-Plane Facade Exporter"
    bl_idname = "MenuFacadeExporter"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):

        layout = self.layout

        facade_exporter = context.scene.facade_exporter

        #Export button
        layout.operator("blender_utils.export_facade")
        layout.prop(facade_exporter, "facade_name")

        layout.separator()

        layout.label(text="Global Properties:")
        layout.prop(facade_exporter, "graded")
        layout.prop(facade_exporter, "ring")
        layout.prop(facade_exporter, "solid")
        layout.prop(facade_exporter, "layergroup")
        layout.prop(facade_exporter, "layergroup_draped")

        layout.separator()

        layout.label(text="Wall Properties:")
        layout.prop(facade_exporter, "render_wall")
        if facade_exporter.render_wall:
            layout.prop(facade_exporter, "wall_texture_alb")
            layout.prop(facade_exporter, "wall_texture_nml")
            layout.prop(facade_exporter, "wall_texture_nml_scale")
        
        layout.separator()

        layout.label(text="Roof Properties:")
        layout.prop(facade_exporter, "render_roof")
        if facade_exporter.render_roof:
            layout.prop(facade_exporter, "roof_texture_alb")
            layout.prop(facade_exporter, "roof_texture_nml")
            layout.prop(facade_exporter, "roof_texture_nml_scale")
            layout.prop(facade_exporter, "roof_height")

        layout.separator()

        layout.label(text="Facade wall Spellings:")

        # Display the collection of text items
        wall_counter = 0
        for index, item in enumerate(facade_exporter.spellings):
            row = layout.row()
            col1 = row.column()
            col2 = row.column()
            
            #We will switch which properties we show based on whether this is a wall or a spelling
            col1.prop(item, "type", text="", expand=False)

            if item.type == "WALL":
                col2.prop(item, "wall_name")
                row2 = layout.row()
                row2.prop(item, "min_width")
                row2.prop(item, "max_width")
                row2.prop(item, "min_heading")
                row2.prop(item, "max_heading")
            elif item.type == "WALL_RULE":
                row2 = layout.row()
                row2.prop(item, "min_width")
                row2.prop(item, "max_width")
                row2.prop(item, "min_heading")
                row2.prop(item, "max_heading")
            else:
                col2.prop(item, "spellings")
            
            row.operator("object.remove_spelling", text="", icon='X').index = index

        # Add button to add new text items
        layout.operator("object.add_spelling", text="Add Spelling")

class BUTTON_export_facade(bpy.types.Operator):
    """Export the X-Plane facade to a file"""
    bl_idname = "blender_utils.export_facade"
    bl_label = "Export X-Plane Facade"

    def execute(self, context):
        #First get the file path, this is the facade name relative to the blender file
        file_path = os.path.join(os.path.dirname(bpy.data.filepath), bpy.context.scene.facade_exporter.facade_name + ".fac")

        #If the file path ends with .fac.fac, remove the last .fac
        if str.endswith(file_path, ".fac.fac"):
            file_path = file_path[:-4]

        #Get the facade text
        facade_text = GetFacade.get_facade()

        #Now write the file
        with open(file_path, "w") as file:
            file.write(facade_text)

        return {'FINISHED'}

