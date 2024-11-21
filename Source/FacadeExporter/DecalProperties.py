#Project: BlenderFacadeExporter
#Author: Connor Russell
#Date: 11/20/2024
#Purpose: Provide a class that contains all the data for a decal

import bpy # type: ignore

from .Helpers.MiscUtils import ftos

#Forced a UI update
def update_ui(self, context):
    context.area.tag_redraw()

class DecalProperties(bpy.types.PropertyGroup):
    enabled: bpy.props.BoolProperty(name="Enabled", description="Whether this decal slot is enabled", update=update_ui)# type: ignore
    alb: bpy.props.StringProperty(name="Decal Albedo", description="The albedo to use in the decal")# type: ignore
    nml: bpy.props.StringProperty(name="Decal Normal", description="The normal to use in the decal (uses RGB keys)")# type: ignore

    projected: bpy.props.BoolProperty(name="Projected", description="Whether the decal's UVs are projected, independant of the base UVs'", update=update_ui)# type: ignore
    tile_ratio: bpy.props.FloatProperty(name="Tile Ratio", description="The ratio of the decal's tiling to the base texture's tiling", default=1.0)# type: ignore
    scale_x: bpy.props.FloatProperty(name="Scale X", description="The scale of the decal in the x direction", default=1.0)# type: ignore
    scale_y: bpy.props.FloatProperty(name="Scale Y", description="The scale of the decal in the y direction", default=1.0)# type: ignore

    dither_ratio: bpy.props.FloatProperty(name="Dither Ratio", description="How much the alpha of the decal modulates the alpha of the base. Probably want this at 0 in a facade...")# type: ignore

    rgb_strength_constant: bpy.props.FloatProperty(name="RGB Strength Constant", description="How strong the RGB decal always is", default=1.0)# type: ignore
    rgb_strength_modulator: bpy.props.FloatProperty(name="RGB Strength Modulator", description="How strong the effect of the keying or modulator texture is on RGB decal's application", default=0.0)# type: ignore

    rgb_decal_key_red: bpy.props.FloatProperty(name="Red key for RGB Decal", description="The red key for the RGB decal key", default=0.0)# type: ignore
    rgb_decal_key_green: bpy.props.FloatProperty(name="Green key for RGB Decal", description="The green key for the RGB decal key", default=0.0)# type: ignore
    rgb_decal_key_blue: bpy.props.FloatProperty(name="Blue key for RGB Decal", description="The blue key for the RGB decal key", default=0.0)# type: ignore
    rgb_decal_key_alpha: bpy.props.FloatProperty(name="Alpha key for RGB Decal", description="The alpha key for the RGB decal key", default=0.0)# type: ignore

    alpha_strength_constant: bpy.props.FloatProperty(name="Alpha Strength Constant", description="How strong the alpha decal always is", default=1.0)# type: ignore
    alpha_strength_modulator: bpy.props.FloatProperty(name="Alpha Strength Modulator", description="How strong the effect of the keying or modulator texture is on alpha decal's application", default=0.0)# type: ignore

    alpha_decal_key_red: bpy.props.FloatProperty(name="Red key for Alpha Decal", description="The red key for the alpha decal key", default=0.0)# type: ignore
    alpha_decal_key_green: bpy.props.FloatProperty(name="Green key for Alpha Decal", description="The green key for the alpha decal key", default=0.0)# type: ignore
    alpha_decal_key_blue: bpy.props.FloatProperty(name="Blue key for Alpha Decal", description="The blue key for the alpha decal key", default=0.0)# type: ignore
    alpha_decal_key_alpha: bpy.props.FloatProperty(name="Alpha key for Alpha Decal", description="The alpha key for the alpha decal key", default=0.0)# type: ignore

    #Internals
    type: bpy.props.StringProperty(name="Decal Type", description="The type of decal this is. Set to BOTH ALB or NML by the parent properties.")# type: ignore
    visible: bpy.props.BoolProperty(name="Visible", description="Whether this decal is visible in the UI", default=True)# type: ignore


    def draw(layout, property_item, index):
        layout.prop(property_item, "enabled", text=f"Decal {index + 1} - " + property_item.type)
        fac_props = bpy.context.scene.facade_exporter

        if property_item.enabled:

            box = layout.box()

            #Textures
            if property_item.type == "BOTH":
                box.prop(property_item, "alb")
                box.prop(property_item, "nml")
            elif property_item.type == "ALB":
                box.prop(property_item, "alb")
            else:
                box.prop(property_item, "nml")

            box.separator()

            #UVs
            row = box.row()
            row.prop(property_item, "projected")

            if property_item.projected:
                row.prop(property_item, "scale_x")
                row.prop(property_item, "scale_y")
            else:
                row.prop(property_item, "tile_ratio")

            box.separator()

            #Dither
            if property_item.type != "NML":
                box.prop(property_item, "dither_ratio")

            box.separator()

            #RGB strength and keying
            box.label(text="RGB Decal Application Control")
            row = box.row()
            row.prop(property_item, "rgb_strength_constant")
            row.prop(property_item, "rgb_strength_modulator")
            row = box.row()
            row.prop(property_item, "rgb_decal_key_red")
            row.prop(property_item, "rgb_decal_key_green")
            row.prop(property_item, "rgb_decal_key_blue")
            row.prop(property_item, "rgb_decal_key_alpha")

            box.separator()

            #Alpha strength and keying. Not present in normal only mode
            if property_item.type != "NML":
                box.label(text="Alpha Decal Application Control")
                row = box.row()
                row.prop(property_item, "alpha_strength_constant")
                row.prop(property_item, "alpha_strength_modulator")
                row = box.row()
                row.prop(property_item, "alpha_decal_key_red")
                row.prop(property_item, "alpha_decal_key_green")
                row.prop(property_item, "alpha_decal_key_blue")
                row.prop(property_item, "alpha_decal_key_alpha")

    def to_string(property_item):
        if (not property_item.visible) or (not property_item.enabled):
            return ""
        
        #Make sure there is a texture specified
        if property_item.alb == "" and property_item.nrm == "":
            return ""
        
        decal_string_alb = ""
        decal_string_nml = ""

        #Start off the decals
        if property_item.projected:
            if (property_item.type == "ALB" or property_item.type == "BOTH") and property_item.alb != "":
                decal_string_alb = "DECAL_PARAMS_PROJ " + ftos(property_item.scale_x, 2) + " " + ftos(property_item.scale_y, 2) + " "
            if (property_item.type == "BOTH" or property_item.type == "NML") and property_item.nrm != "":
                decal_string_nml = "NORMAL_DECAL_PARAMS_PROJ " + ftos(property_item.scale_x, 2) + " " + ftos(property_item.scale_y, 2) + " "
        else:
            if (property_item.type == "ALB" or property_item.type == "BOTH") and property_item.alb != "":
                decal_string_alb = "DECAL_PARAMS " + ftos(property_item.tile_ratio, 2) + " "
            if (property_item.type == "BOTH" or property_item.type == "NML") and property_item.nrm != "":
                decal_string_nml = "NORMAL_DECAL_PARAMS " + ftos(property_item.tile_ratio, 2) + " "

        #For readability
        p = property_item

        #Finish off the albedo
        if decal_string_alb != "":
            decal_string_alb += (str(p.dither_ratio) + " " +
                                 str(p.rgb_decal_key_red) + " " + str(p.rgb_decal_key_green) + " " + str(p.rgb_decal_key_blue) + " " + str(p.rgb_decal_key_alpha) + " " +
                                 str(p.rgb_strength_modulator) + " " + str(p.rgb_strength_constant) + " " +
                                 str(p.alpha_decal_key_red) + " " + str(p.alpha_decal_key_green) + " " + str(p.alpha_decal_key_blue) + " " + str(p.alpha_decal_key_alpha) + " " +
                                 str(p.alpha_strength_modulator) + " " + str(p.alpha_strength_constant) + " " + p.alb)

        #Finish off the normal
        if decal_string_nml != "":
            decal_string_nml += (str(p.rgb_decal_key_red) + " " + str(p.rgb_decal_key_green) + " " + str(p.rgb_decal_key_blue) + " " + str(p.rgb_decal_key_alpha) + " " +
                                 str(p.rgb_strength_modulator) + " " + str(p.rgb_strength_constant) + p.nml)
            
        return decal_string_alb + "\n" + decal_string_nml

        