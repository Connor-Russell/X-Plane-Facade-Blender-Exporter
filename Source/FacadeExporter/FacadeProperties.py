#Project: BlenderFacadeExporter
#Author: Connor Russell
#Date: 11/14/2024
#Purpose: Contains the properties for the whole facade in Blender. There can only be one facade per file.

import bpy  # type: ignore
import os

from . import GetFacade
from . import DecalProperties
from bpy.app.handlers import persistent # type: ignore

#Forced a UI update
def update_ui(self, context):
    context.area.tag_redraw()

#Functions that update the state of the decals.
def update_wall_decals(self, context):
    seperate = bpy.context.scene.facade_exporter.wall_seperate_normal_decals
    if seperate:
        #Set the first 4 decals to be visible, first 2 to alb, second 2 to nml
        for i in range(4):
            bpy.context.scene.facade_exporter.wall_decals[i].visible = True
            bpy.context.scene.facade_exporter.wall_decals[i].type = "ALB" if i < 2 else "NML"
    else:
        #Set the first 2 decals to be visible, both to both, last 2 to not visible
        for i in range(4):
            bpy.context.scene.facade_exporter.wall_decals[i].visible = i < 2
            bpy.context.scene.facade_exporter.wall_decals[i].type = "BOTH"

def update_roof_decals(self, context):
    seperate = bpy.context.scene.facade_exporter.roof_seperate_normal_decals
    if seperate:
        #Set the first 4 decals to be visible, first 2 to alb, second 2 to nml
        for i in range(4):
            bpy.context.scene.facade_exporter.roof_decals[i].visible = True
            bpy.context.scene.facade_exporter.roof_decals[i].type = "ALB" if i < 2 else "NML"
    else:
        #Set the first 2 decals to be visible, both to both, last 2 to not visible
        for i in range(4):
            bpy.context.scene.facade_exporter.roof_decals[i].visible = i < 2
            bpy.context.scene.facade_exporter.roof_decals[i].type = "BOTH"

#This get's called after everything is loaded to give us 4 decals. We should only *ever* have 4 as X-Plane has a fixed number of slots (2 alb 2 nml), and this also simplifies the rest of our code because we can assume we have 4.
@persistent
def set_four_decals(dummy):
    print("Validating collection size")
    scene = bpy.context.scene
    facade_exporter = scene.facade_exporter
    while len(facade_exporter.wall_decals) < 4:
        facade_exporter.wall_decals.add()
    while len(facade_exporter.wall_decals) > 4:
        facade_exporter.wall_decals.remove(len(facade_exporter.wall_decals) - 1)
    
    while len(facade_exporter.roof_decals) < 4:
        facade_exporter.roof_decals.add()
    while len(facade_exporter.roof_decals) > 4:
        facade_exporter.roof_decals.remove(len(facade_exporter.roof_decals) - 1)

    update_wall_decals(None, None)
    update_roof_decals(None, None)

class FacadeSpellingItem(bpy.types.PropertyGroup):
    type: bpy.props.EnumProperty(
        name="Type",
        items=[
            ("WALL", "Wall", "Wall definition"),
            ("WALL_RULE ", "Wall Rule", "Second wall rule"),
            ("SPELLING", "Spelling", "Wall spelling")
        ],
        update=update_ui)# type: ignore
    min_width: bpy.props.FloatProperty(name="Min Width", description="The minimum width of the wall")# type: ignore
    max_width: bpy.props.FloatProperty(name="Max Width", description="The maximum width of the wall")# type: ignore
    min_heading: bpy.props.FloatProperty(name="Min Heading", description="The minimum heading of the wall")# type: ignore
    max_heading: bpy.props.FloatProperty(name="Max Heading", description="The maximum heading of the wall")# type: ignore
    spellings: bpy.props.StringProperty(name="Spellings", default="", update=update_ui)# type: ignore
    wall_name: bpy.props.StringProperty(name="Wall Name", default="", update=update_ui)# type: ignore

#Class containing the properties for the UI
class PROP_facade_exporter(bpy.types.PropertyGroup):

    #Facade name
    facade_name: bpy.props.StringProperty( name="Facade Name", description="The name of the facade")# type: ignore

    #Global properties
    graded: bpy.props.BoolProperty(name="Graded", description="Whether the facade is graded, otherwise draped")# type: ignore
    ring: bpy.props.BoolProperty(name="Ring", description="Whether the facade is a closed or an open ring")# type: ignore
    layergroup: bpy.props.StringProperty(name="Layer Group", description="The layer group of the facade")# type: ignore
    layergroup_draped: bpy.props.StringProperty(name="Layer Group Draped", description="The layer group of the draped facade")# type: ignore
    solid: bpy.props.BoolProperty(name="Solid", description="Whether the roof has collision testing enabled")# type: ignore

    #Wall properties
    render_wall: bpy.props.BoolProperty(name="Render Wall", description="Whether the wall is rendered", update=update_ui)# type: ignore
    wall_texture_alb: bpy.props.StringProperty(name="Texture ALB Path", description="The relative path of the ALB", subtype='FILE_PATH')# type: ignore
    wall_texture_nml: bpy.props.StringProperty(name="Texture NML Path", description="The relative path of the NML", subtype='FILE_PATH')# type: ignore
    wall_texture_nml_scale: bpy.props.FloatProperty(name="Texture NML Scale", description="The scale of the NML texture")# type: ignore

    #Roof properties
    render_roof: bpy.props.BoolProperty(name="Render Roof", description="Whether the roof is rendered", update=update_ui)# type: ignore
    roof_texture_alb: bpy.props.StringProperty(name="Texture ALB Path", description="The relative path of the ALB", subtype='FILE_PATH')# type: ignore
    roof_texture_nml: bpy.props.StringProperty(name="Texture NML Path", description="The relative path of the NML", subtype='FILE_PATH')# type: ignore
    roof_texture_nml_scale: bpy.props.FloatProperty(name="Texture NML Scale", description="The scale of the NML texture")# type: ignore
    roof_height: bpy.props.FloatProperty(name="Roof Height", description="The height of the roof")# type: ignore

    #Spellings
    spellings: bpy.props.CollectionProperty(type=FacadeSpellingItem)# type: ignore

    #Decals
    wall_modulator_texture: bpy.props.StringProperty(name="Wall Modulator Texture", description="The texture that modulates the wall", subtype='FILE_PATH')# type: ignore
    wall_seperate_normal_decals: bpy.props.BoolProperty(name="Wall Seperate Normal Decals", description="Whether the wall has seperate normal decals, otherwise normals align with the RGB decal.", update=update_wall_decals)# type: ignore
    wall_decals: bpy.props.CollectionProperty(type=DecalProperties.DecalProperties)# type: ignore
    roof_modulator_texture: bpy.props.StringProperty(name="Roof Modulator Texture", description="The texture that modulates the roof", subtype='FILE_PATH')# type: ignore
    roof_seperate_normal_decals: bpy.props.BoolProperty(name="Roof Seperate Normal Decals", description="Whether the roof has seperate normal decals, otherwise normals align with the RGB decal.", update=update_wall_decals) # type: ignore
    roof_decals: bpy.props.CollectionProperty(type=DecalProperties.DecalProperties) # type: ignore

#Classes that add/remove spellings
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

    index: bpy.props.IntProperty()# type: ignore

    def execute(self, context):
        context.scene.facade_exporter.spellings.remove(self.index)
        return {'FINISHED'}
    
#Class that creates the UI
class MENU_facade_exporter(bpy.types.Panel):
    """Creates a Panel in the scene properties window"""
    bl_label = "X-Plane Facade Exporter"
    bl_idname = "SCENE_PT_facade_exporter"
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

        #Wall properties-----------------------------------------------------------------------------------------

        box = layout.box()

        box.label(text="Wall Properties:")
        box.prop(facade_exporter, "render_wall")
        if facade_exporter.render_wall:
            box.prop(facade_exporter, "wall_texture_alb")
            box.prop(facade_exporter, "wall_texture_nml")
            box.prop(facade_exporter, "wall_texture_nml_scale")
            
            box.separator()

            #Decals
            box.prop(facade_exporter, "wall_seperate_normal_decals")
            box.prop(facade_exporter, "wall_modulator_texture")
            for index, item in enumerate(facade_exporter.wall_decals):
                if item.visible:
                    DecalProperties.DecalProperties.draw(box, item, index)
        

        layout.separator()

        #Roof properties-----------------------------------------------------------------------------------------

        box = layout.box()

        box.label(text="Roof Properties:")
        box.prop(facade_exporter, "render_roof")
        if facade_exporter.render_roof:
            box.prop(facade_exporter, "roof_texture_alb")
            box.prop(facade_exporter, "roof_texture_nml")
            box.prop(facade_exporter, "roof_texture_nml_scale")
            box.prop(facade_exporter, "roof_height")

            box.separator()

            #Decals
            box.prop(facade_exporter, "roof_seperate_normal_decals")
            box.prop(facade_exporter, "roof_modulator_texture")
            for index, item in enumerate(facade_exporter.roof_decals):
                if item.visible:
                    DecalProperties.DecalProperties.draw(box, item, index)

        layout.separator()

        #Wall spettings-----------------------------------------------------------------------------------------

        box = layout.box()

        box.label(text="Facade Wall Spellings:")

        # Display the collection of text items
        wall_counter = 0
        for index, item in enumerate(facade_exporter.spellings):
            row = box.row()
            col1 = row.column()
            col2 = row.column()
            
            #We will switch which properties we show based on whether this is a wall or a spelling
            col1.prop(item, "type", text="", expand=False)

            if item.type == "WALL":
                col2.prop(item, "wall_name")
                row2 = box.row()
                row2.prop(item, "min_width")
                row2.prop(item, "max_width")
                row2.prop(item, "min_heading")
                row2.prop(item, "max_heading")
            elif item.type == "WALL_RULE":
                row2 = box.row()
                row2.prop(item, "min_width")
                row2.prop(item, "max_width")
                row2.prop(item, "min_heading")
                row2.prop(item, "max_heading")
            else:
                col2.prop(item, "spellings")
            
            row.operator("object.remove_spelling", text="", icon='X').index = index

        # Add button to add new text items
        box.operator("object.add_spelling", text="Add Spelling")

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

