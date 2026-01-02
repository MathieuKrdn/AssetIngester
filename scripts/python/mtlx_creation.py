"""
Material Builder for Houdini

This module creates MaterialX shader networks in Houdini.
It builds a complete PBR material with albedo, roughness, normal, metallic, and displacement maps.

Functions:
    createMtlx(hda, materialName, parm): Creates a MaterialX material subnet with connected texture nodes
"""

import hou

def createMtlx(hda, materialName, parm):

    matLib = hda.node("materiallibrary")
    material = matLib.createNode("subnet",materialName)
    material.moveToGoodPosition()

    #---- Create MaterialX nodes ----
    subnetConnectorSurface = material.createNode("subnetconnector", "surface_output")
    subnetConnectorSurface.parm("connectorkind").set(1)
    subnetConnectorSurface.parm("parmname").set("surface")
    subnetConnectorSurface.parm("parmlabel").set("Surface")
    subnetConnectorSurface.parm("parmtype").set(24)

    subnetConnectorDisplacement = material.createNode("subnetconnector", "displacement_output")
    subnetConnectorDisplacement.parm("connectorkind").set(1)
    subnetConnectorDisplacement.parm("parmname").set("displacement")
    subnetConnectorDisplacement.parm("parmlabel").set("Displacement")
    subnetConnectorDisplacement.parm("parmtype").set(25)

    surface = material.createNode("mtlxstandard_surface", "mtlxstandard_surface")

    albedoImage = material.createNode("mtlximage", "Albedo")
    roughnessImage = material.createNode("mtlximage", "Roughness")
    normalImage = material.createNode("mtlximage", "Normal")
    metallicImage = material.createNode("mtlximage", "Metallic")
    displaceImage = material.createNode("mtlximage", "Displacement")

    displacement = material.createNode("mtlxdisplacement", "mtlxdisplacement")
    normalMap = material.createNode("mtlxnormalmap::2.0", "mtlxnormalmap")

    #---- Create connections ----
    subnetConnectorSurface.setNamedInput("suboutput", surface, "out")
    subnetConnectorDisplacement.setNamedInput("suboutput", displacement, "out")
    surface.setNamedInput("specular_roughness", roughnessImage, "out")
    displacement.setNamedInput("displacement", displaceImage, "out")
    surface.setNamedInput("base_color", albedoImage, "out")
    surface.setNamedInput("normal", normalMap, "out")
    surface.setNamedInput("metalness", metallicImage, "out")
    normalMap.setNamedInput("in", normalImage, "out")
    material.layoutChildren()

    #---- Declare connections with the future HDA ----
    albedoImage.parm("file").set(hda.eval("albedo"+parm))
    albedoImage.parm("signature").set("Color")
    albedoImage.parm("filecolorspace").set(hda.eval("colorspace"+parm))

    roughnessImage.parm("file").set(hda.eval("roughness"+parm))
    roughnessImage.parm("signature").set("Float")

    metallicImage.parm("file").set(hda.eval("metalness"+parm))
    metallicImage.parm("signature").set("Float")

    normalImage.parm("file").set(hda.eval("normal"+parm))
    normalImage.parm("signature").set("Vector2")

    displaceImage.parm("file").set(hda.eval("displacement"+parm))
    displaceImage.parm("signature").set("Float")

    material.setGenericFlag(hou.nodeFlag.Material, True)

#--------------- LAUNCH ---------------    
hda = hou.node("/stage/subnet1")
materialName = "test"
parm = kwargs['parm'][-3:]

if hda.node(f"materiallibrary/{materialName}"):
    print(f"Material '{materialName}' already exists")
    material = hda.node(f"materiallibrary/{materialName}/mtlxstandard_surface")
    material.setCurrent(True, clear_all_selected=True)
    hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor).setCurrentNode(material)
else:
    createMtlx(hda, materialName, parm)
    print(f"Created MaterialX material '{materialName}' in material library 'materiallibrary'")
