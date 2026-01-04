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
    albedo_parm = hda.parm("albedo__"+parm)
    if albedo_parm:
        albedoImage.parm("file").set(albedo_parm)
        albedoImage.parm("signature").set(0)
    
    colorspace_parm = hda.parm("colorspace__"+parm)
    if colorspace_parm:
        albedoImage.parm("filecolorspace").set(colorspace_parm)
        roughnessImage.parm("filecolorspace").set(colorspace_parm)
        metallicImage.parm("filecolorspace").set(colorspace_parm)
        normalImage.parm("filecolorspace").set(colorspace_parm)
        displaceImage.parm("filecolorspace").set(colorspace_parm)

    roughness_parm = hda.parm("roughness__"+parm)
    if roughness_parm:
        roughnessImage.parm("file").set(roughness_parm)
        roughnessImage.parm("signature").set("Float")

    metalness_parm = hda.parm("metalness__"+parm)
    if metalness_parm:
        metallicImage.parm("file").set(metalness_parm)
        metallicImage.parm("signature").set("Float")

    normal_parm = hda.parm("normal__"+parm)
    if normal_parm:
        normalImage.parm("file").set(normal_parm)
        normalImage.parm("signature").set("Color")

    displacement_parm = hda.parm("displacement__"+parm)     
    if displacement_parm:
        displaceImage.parm("file").set(displacement_parm)
        displaceImage.parm("signature").set("Color")

    displacement_scale_parm = hda.parm("dispScale__"+parm)
    if displacement_scale_parm:
        displacement.parm("scale").set(displacement_scale_parm)

    normalMap_scale_parm = hda.parm("normalScale__"+parm)
    if normalMap_scale_parm:
        normalMap.parm("scale").set(normalMap_scale_parm)

    material.setGenericFlag(hou.nodeFlag.Material, True)

def material(node, kwargs):
    """Main function called from HDA callback to create or navigate to material"""
    hda = hou.node(".")
    parm = kwargs['parm'].name()[-3:]
    materialName = hda.parm("materialName_"+parm).eval()
    
    if hda.node(f"materiallibrary/{materialName}"):
        print(f"Material '{materialName}' already exists")
        material_node = hda.node(f"materiallibrary/{materialName}/mtlxstandard_surface")
        material_node.setCurrent(True, clear_all_selected=True)
        hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor).setCurrentNode(material_node)
    else:
        createMtlx(hda, materialName, parm)
        material_node = hda.node(f"materiallibrary/{materialName}/mtlxstandard_surface")
        if material_node:
            material_node.setCurrent(True, clear_all_selected=True)
            hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor).setCurrentNode(material_node)
        print(f"Created MaterialX material '{materialName}' in material library 'materiallibrary'")


       