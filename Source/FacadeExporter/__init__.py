#Project:   X-PlaneFacadeExporter
#Author:    Connor Russell
#Date:      6/30/2023
#Purpose:   Provides a simple WYSIWYG interface for exporting facades from Blender to X-Plane.

#Blender plugin info
bl_info = {
    "name": "X-Plane Facade Exporter",
    "author": "Connor Russell",
    "version": (0, 9),
    "blender": (3, 1, 0),
    "location": "Properties > Scene > X-Plane Facade Exporter",
    "description": "Unofficial Blender addon to exporter for X-Plane facades.",
    "git_url": "https://github.com/Connor-Russell/X-Plane-Blender-Facade-Exporter",
    "category": "Import-Export"
}

#System modules
import os

#Blender api
import bpy

#Our modules
from . import FacadeProperties
from . import ObjectProperties

#List of all classes to register
classes = (
    FacadeProperties.MENU_facade_exporter,
    FacadeProperties.BUTTON_export_facade,
    ObjectProperties.MENU_facade_object,
    FacadeProperties.MENU_BT_facade_exporter_add_spelling,
    FacadeProperties.MENU_BT_facade_exporter_remove_spelling
)

def register():

    #Register the spelling item type
    bpy.utils.register_class(FacadeProperties.FacadeSpellingItem)

    #Facade wide properties
    bpy.utils.register_class(FacadeProperties.PROP_facade_exporter)
    bpy.types.Scene.facade_exporter = bpy.props.PointerProperty(type=FacadeProperties.PROP_facade_exporter)

    #Object specific properties
    bpy.utils.register_class(ObjectProperties.PROP_facade_object)
    bpy.types.Object.facade_object = bpy.props.PointerProperty(type=ObjectProperties.PROP_facade_object)

    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():

    del bpy.types.Scene.facade_exporter

    for cls in classes:
        bpy.utils.unregister_class(cls)

    bpy.utils.unregister_class(FacadeProperties.PROP_facade_exporter)
    bpy.utils.unregister_class(ObjectProperties.PROP_facade_object)
    bpy.utils.unregister_class(FacadeProperties.FacadeSpellingItem)

if __name__ == "__main__":
    register()