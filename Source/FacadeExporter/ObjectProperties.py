#Project: BlenderFacadeExporter
#Author: Connor Russell
#Date: 11/14/2024
#Purpose: Contains the properties for objects in Blender, which vary based on whether this is a mesh object (exported as a mesh into the .fac) or an empty (an attached obj). Every object contains the properties, but they are shown and hidden dynamically

import bpy

#Class containing the properties for the UI
class PROP_facade_object(bpy.types.PropertyGroup):

    #Number of cuts for the mesh
    far_lod: bpy.props.IntProperty(name="Far LOD", description="The far LOD for the object", default=1000)
    group: bpy.props.IntProperty(name="Group", description="The group for the object. Use for layering transparency")
    cuts: bpy.props.IntProperty(name="Cuts", description="The number of cuts for the mesh (used for curves)")
    exportable: bpy.props.BoolProperty(name="Exportable", description="Whether the object is exportable", default=True)
    draped: bpy.props.BoolProperty(name="Draped", description="Whether the object is draped", default=False)
    resource: bpy.props.StringProperty(name="Resource", description="The resource for the object")
    
#Class that creates the UI
class MENU_facade_object(bpy.types.Panel):
    """Creates a Panel in the object properties window"""
    bl_label = "X-Plane Facade Exporter"
    bl_idname = "MenuFacadeObject"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):

        layout = self.layout

        facade_object = context.object.facade_object

        #If this is a mesh, we show the mesh options of cut, and exportable
        if context.object.type == 'MESH':
            layout.label(text="Facade Mesh Properties")
            layout.separator()
            layout.prop(facade_object, "far_lod")
            layout.prop(facade_object, "group")
            layout.prop(facade_object, "cuts")
            layout.prop(facade_object, "exportable")

        elif context.object.type == 'EMPTY':
            layout.label(text="Facade Attached Object Properties")
            layout.separator()
            layout.prop(facade_object, "exportable")
            layout.prop(facade_object, "draped")
            layout.prop(facade_object, "resource")

        else:
            layout.label(text="This object is not a mesh or empty")
