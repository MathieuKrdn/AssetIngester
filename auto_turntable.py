import hou
import math
from pxr import Usd, UsdGeom, Gf

def auto_turntable(asset, camera, focal, aperture, padding, node, stage):
    #calculate the bounds
    bbox_cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), [UsdGeom.Tokens.default_])
    geo_prim = stage.GetPrimAtPath(asset)

    if geo_prim:
        world_bbox = bbox_cache.ComputeWorldBound(geo_prim)
        range_box = world_bbox.GetRange()
        center = range_box.GetMidpoint()
        size = range_box.GetSize()
        max_dim = max(size[0], size[1], size[2])

        # distance
        focal = 35.0
        aperture = 36.0
        fov_rad = 2 * math.atan(aperture / (2 * focal))
        distance = (max_dim * padding) / math.tan(fov_rad / 2)

        #set the cam
        cam_prim = UsdGeom.Camera.Define(stage, camera_path)
        cam_xform = UsdGeom.Xformable(cam_prim)
        cam_xform.ClearXformOpOrder()
        cam_translate = cam_xform.AddTranslateOp()
        cam_translate.Set(Gf.Vec3d(center[0], center[1], center[2] + distance))

        #set the turntable animation
        rotate_prim = UsdGeom.Xform.Define(stage, asset)
        rotate_xform = UsdGeom.Xformable(rotate_prim)
        rotate_op = rotate_xform.AddRotateYOp()
        
        start_frame = hou.playbar.frameRange()[0]
        end_frame = hou.playbar.frameRange()[1]

        for frame in range(int(start_frame), int(end_frame) + 1):
            angle = (frame - start_frame) * (360.0 / (end_frame - start_frame))
            rotate_op.Set(angle, Usd.TimeCode(frame))
    else:
        hou.ui.displayMessage(f"Prim not found at {asset}")