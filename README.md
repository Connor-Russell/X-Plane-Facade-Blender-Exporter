# X-Plane Blender Facade Exporter
# ATTENTION
This plugin has been replaced with a far more [comprehensive plugin](https://github.com/Connor-Russell/Blender-X-Plane-Extensions). Please use the new plugin - this repo is unmaintained!
## A minimalist exporter for X-Plane facades
### By Connor Russell
This tool provide a simple WYSIWYG way to export geometry, and attached objects, into an X-Plane facade. Currently, this tool only exports **Type 2** facades, and only exports **meshes**, **roof objects**, and **attached objects**, and of course the facade headers and spellings. Different floor heights, and facade-scrapers are not supported. Automatic creation of wall rules or spellings is not supported. Below is basic documention on how to use the tool to create facades in Blender, however it is strongly advised you **first** familiarize yourself with the [X-Plane facade format](https://developer.x-plane.com/article/x-plane-10-facade-fac-file-format-specification/), specifically **type 2 facades**.

## Supported Blender Versions
 - Blender 2.93-4.01: Full
 - Blender 4.1-4.23: Partial. Normals are not properly translated when an object has a rotation transformation.
 - If it does not work on a listed version please let me know!

## Install
- Download the latest release
- Go to your Blender settings, then the addon page
- Click the install button, and choose the downloaded .zip
- Search for FacadeExporter in the addon list and enable it

## Coordinate Orientation
**NEGATIVE Y:** This is lengthways (parallel) along the facade wall. Please note it is **negative**, *not* positive Y. 0 Y is the start of a wall, negative \<your wall length\> Y is the end

**Positive X:** This is extruding perpendicular, away from the wall.

**Positive Z:** This is up.

## Segments
X-Plane facades are made of segments. In this tool, Blender **collections** are the equivalent of a X-Plane facade **segment**.

X-Plane facades have two versions of a segment for every type of segment, the basic version, and the curved version. This allows you to have more cuts in the curved vesion (for smoother cuts), without having the extra geometry on straight segments.

This tool will automatically generate the curved segment, unless you specify a custom curved segment. You can specify a custom curved segment by naming the collection <my segment name **_curved**> (this is not case sensitive).

## Meshes
A X-Plane facade segment consists of **meshes** and **attached objects** (discussed in the next section). In this tool, Blender **objects** are the equivalent of a X-Plane facade **mesh**.

Every blender object has properties under the "X-Plane Facade Exporter" section in the "Object Properties" (the orange square in the Blender properties pane). The properties are:

**Exportable:** Defaults to true. Uncheck this if you don't want this specific object being included in the facade. This can be useful to disable meshes you are using for reference purposes only.

**Far LOD:** How far out this mesh will draw. You can use multiple meshes with different Far LODs to create additive LODs in your walls. **Remember:** Facades are NOT instanced, so be sparing on your geometry, and LODs, otherwise you may melt your customer's GPUs!

**Group:** What draw group this mesh is in (useful for transparency). Keep in mind groups are *not* maintained between LODs

**Segments:** How many segments this mesh has lengthways. This is used for curves. If my mesh is a plane with 4 verticies, it has 1 segment. If I subdivide the edges that are running lengthways (positive Y axis) twice, my mesh now has 3 segments, and will curve at those 2 points on curved facade edges. More segments obviously result in smoother curves.

## Attached Object
X-Plane facade segments, and roofs, can have attached objects. These are references to X-Plane .obj's, that are place at a relative position along a wall, or on the roof. In this addon, **empties** are the quivalent of a X-Plane facade **attached object**

Every empty has the following properties:

**Exportable:** Defaults to true. Uncheck this if you don't want this attached object being included in the facade.

**Draped:** Whether you want this object to sit on the ground. If false, the object will be "graded" - that is, it's altitude will be that of the facade's mesh at that point (which is either interpolated between the end nodes if the facade is draped, or the altitude of the whole facade if the facade is graded.

**Resource:** This is what object is attached here. This can be a real path relative to your facade file, or an X-Plane library path

## Facade Parameters
This addon supports a single facade per Blender file. The facade's properties are located in the "X-Plane Facade Exporter" tab of the "Scene Properties" in the Blender Properties window. The following properties are available:
**Facade Name:** This is the facade's name, it is a relative path to the Blender file (so something like "../Fence.fac" is acceptable). The .fac extension is not required in the name, but it is allowed.

**Graded:** Whether the facade should be graded (setting the entire facade's elevation at the altitude of the center of the first wall). Defaults to off (draped) where each node's altitude is based on the terrain under it. Use graded for buildings, and draped for fences.

**Ring:** Whether the facade is closed. 

**Solid:** Whether the roof of the facade has collision testing enabled in X-Plane.

**Layer Group:** The X-Plane layer group to draw in (useful for managing transparency)

**Layer Group Draped:** The layer group of the roof if it is draped, just like in your .pols

### Wall Properties:

**Render Wall:** Whether there should be any wall geometry *rendered*. Note you MUST have wall geometry for X-Plane to calculate layouts. Disabling this just disabled rendering of the walls in X-Plane.

**Texture ALB Path:** The path for your albedo texture, relative to your facade file.

**Texture NML Path:** The path for your normal map texture, relative to your facade file.

**Texture NML Scale:** How many times your normal map repeats to one repetition of your albedo. Just like TEXTURE_NORMAL in your polygons.

**Decals:** These settings allow you to add custom [decals](https://developer.x-plane.com/article/using-decals-to-add-detail-to-scenery/). There are 4 decal slots, 2 for the albedo, 2 for the normal. By default these are combined, but checking the box "Seperate Normal Decals" will allow you to control the normal and albedo decals independantly. Next to each decal slot it is indicated it's purpose, BOTH, ALB (albedo), or NML (normal). When in both mode, the RGB decal keys will be used for the normal map keys. 

### Roof Properties:

**Render Wall:** Whether there should be any roof geometry rendered in sim.

**Texture ALB Path:** The path for your albedo texture, relative to your facade file.

**Texture NML Path:** The path for your normal map texture, relative to your facade file.

**Texture NML Scale:** How many times your normal map repeats to one repetition of your albedo. Just like TEXTURE_NORMAL in your polygons.

**Decals:** These settings allow you to add custom [decals](https://developer.x-plane.com/article/using-decals-to-add-detail-to-scenery/). There are 4 decal slots, 2 for the albedo, 2 for the normal. By default these are combined, but checking the box "Seperate Normal Decals" will allow you to control the normal and albedo decals independantly. Next to each decal slot it is indicated it's purpose, BOTH, ALB (albedo), or NML (normal). When in both mode, the RGB decal keys will be used for the normal map keys. 

## Spellings
For a full understanding of Spellings, please see the [X-Plane documentation](https://developer.x-plane.com/article/x-plane-10-facade-fac-file-format-specification/)

You can add wall definitions and spellings in the Facade properties. Click the "Add Spelling" button to add a spelling. Once you've added a spelling you can choose whether it is a wall, additional wall rule (you can only have 1 extra wall rule, but this addon does not enforce this rule), or a spelling.

Wall rules have a name, a min/max length/heading, the length/heading rules only apply if "Pick Walls" is disabled in WED for this facade. The name is what you will see what chooseing the wall in WED, so name it clearly! All spellings that follow until the next Wall will belong to this wall.

A spelling defines an order of segments that can be used to fill out the wall. X-Plane will choose a combinations of spellings based on which ones result in the minimum amount of stretch, so it's good to have a variety of segments with different lengths, and a variety of spellings chaining these segments together. Prefer fewer longer segments over many small segments, to reduce the amount of geometry drawn. 

Spellings are a space seperated list of zero-based segment indexs. I.e. a spelling of "1 0" represents using the second wall, then the first wall. This space seperated list of zero-based segment indicies is what you should enter in the "Spelling" field of your Spelling in the facade properties. The syste, sounds very complicated at first, but once you've used it a couple times, you'll find it quite easy and very powerful.

### Project Notes for Developers

Build.ps1 copies the files into the Blender directories, you will need to change the paths to match your system.

Test.ps1 runs automated tests on all Blender versions specified, you will need to adjust file paths for your system. Test.ps1 will call Build.ps1 before testing, to ensure the addon is up to date.

There are run configurations in VS Code to run the build.ps1 and test.ps1 scripts.
