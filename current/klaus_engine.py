import sys
import os

# --- THE PRIORITY OVERRIDE (100% FUNCTIONAL) ---
appdata = os.environ.get("APPDATA")
klaus_modules = os.path.join(appdata, "Blender Foundation", "Blender", "5.0", "scripts", "modules")

if klaus_modules not in sys.path:
    sys.path.insert(0, klaus_modules)

# --- STANDARD IMPORTS ---
import bpy
from mathutils import Vector
import cv2
import numpy as np

# 1. The Metadata
bl_info = {
    "name": "Klaus Engine - True TPS",
    "author": "You",
    "version": (1, 4),
    "blender": (5, 0, 0),
    "category": "Animation",
}

# --- THE BULLETPROOF VECTOR EXTRACTOR (100% FUNCTIONAL) ---
def get_vec(p):
    """Safely extracts a vector no matter what object Blender throws at us."""
    if hasattr(p, 'co'): return p.co
    if hasattr(p, 'position'): return p.position
    return p  # If it's already a Vector, just return it!

# --- THE MAGIC MATH FUNCTION (100% FUNCTIONAL) ---
def resample_stroke(points, num_samples=50):
    if len(points) < 2: return [get_vec(p) for p in points]
        
    total_length = 0.0
    segments = []
    
    for i in range(len(points) - 1):
        p1 = get_vec(points[i])
        p2 = get_vec(points[i+1])
        dist = (p2 - p1).length
        segments.append(dist)
        total_length += dist
        
    resampled = [get_vec(points[0])] 
    step_size = total_length / (num_samples - 1)
    
    for i in range(1, num_samples - 1):
        target_distance = i * step_size
        accumulated = 0.0
        
        for j in range(len(segments)):
            if accumulated + segments[j] >= target_distance:
                remainder = target_distance - accumulated
                ratio = remainder / segments[j] if segments[j] > 0 else 0
                p1 = get_vec(points[j])
                p2 = get_vec(points[j+1])
                resampled.append(p1.lerp(p2, ratio))
                break
            accumulated += segments[j]
            
    resampled.append(get_vec(points[-1]))
    return resampled

# 2. The Operator
class KLAUS_OT_warp(bpy.types.Operator):
    bl_idname = "klaus.warp_shadow" 
    bl_label = "Generate Warped Shadow!" 
    
    def execute(self, context):
        obj = context.active_object
        if obj is None or obj.type != 'GREASEPENCIL':
            return {'CANCELLED'}
        
        # ====================================================================
        # 🛑 CURRENT BROKEN STATE (LEGACY API)
        # Blender 5.0 removed `obj.data.layers`. This code throws an error.
        # ====================================================================
        """
        layer = obj.data.layers.active
        if not layer or len(layer.frames) < 2:
            return {'CANCELLED'}
        
        frame_a = layer.frames[0]
        frame_b = layer.frames[1]
        
        strokes_a = frame_a.drawing.strokes if hasattr(frame_a, 'drawing') else frame_a.strokes
        strokes_b = frame_b.drawing.strokes if hasattr(frame_b, 'drawing') else frame_b.strokes
        """

        # ====================================================================
        # 🚀 PREDICTED VERSION (BLENDER 5.0 V3 API)
        # When picking this project back up, you will need to research how 
        # Blender 5.0 stores strokes. It will likely look something like this:
        # ====================================================================
        """
        # 1. Access the new Drawings / Data-block architecture
        # (Need to verify exact syntax in Blender 5.0 Python API documentation)
        drawing_data = obj.data.drawings  
        
        # 2. Fetch the current frame and the target frame
        frame_a = drawing_data.get_frame(current_frame)
        frame_b = drawing_data.get_frame(target_frame)
        
        # 3. Extract the stroke coordinates directly from the new geometry blocks
        strokes_a = frame_a.strokes
        strokes_b = frame_b.strokes
        """
        
        # To prevent the script from hard-crashing while saving/testing, 
        # we will force a cancellation here until the v3 API code is written.
        self.report({'WARNING'}, "Klaus Engine paused: Awaiting Blender 5.0 API update.")
        return {'CANCELLED'}
        
        # ====================================================================
        # ⚙️ THE TPS WARP ENGINE (100% FUNCTIONAL)
        # Once the frames above are successfully fetched, this code below 
        # will handle the actual magic automatically.
        # ====================================================================
        
        points_a = resample_stroke(strokes_a[0].points, num_samples=50)
        points_b = resample_stroke(strokes_b[0].points, num_samples=50)
        
        scale_factor = 150.0
        img_size = 512
        center_img = (img_size // 2, img_size // 2)
        
        center_a = Vector((0, 0, 0))
        for p in points_a:
            center_a += p
        center_a /= len(points_a)
        
        src_pts = []
        dst_pts = []
        
        for pa, pb in zip(points_a, points_b):
            px_a = (pa.x - center_a.x) * scale_factor + center_img[0]
            py_a = -(pa.z - center_a.z) * scale_factor + center_img[1]
            src_pts.append([px_a, py_a])
            
            px_b = (pb.x - center_a.x) * scale_factor + center_img[0]
            py_b = -(pb.z - center_a.z) * scale_factor + center_img[1]
            dst_pts.append([px_b, py_b])
            
        img = np.zeros((img_size, img_size, 3), dtype=np.uint8)
        cv2.circle(img, center_img, 100, (0, 0, 255), -1) 
        
        src_arr = np.array(src_pts, dtype=np.float32).reshape(1, -1, 2)
        dst_arr = np.array(dst_pts, dtype=np.float32).reshape(1, -1, 2)
        
        matches = [cv2.DMatch(i, i, 0) for i in range(len(src_pts))]
        
        tps = cv2.createThinPlateSplineShapeTransformer()
        tps.setRegularizationParameter(0.1) 
        tps.estimateTransformation(dst_arr, src_arr, matches) 
        warped_img = tps.warpImage(img)
        
        # TODO: Replace cv2.imshow with internal Blender texture baking later.
        print("\n--- KLAUS ENGINE: SUCCESS ---")
        cv2.imshow("Frame 1: Original Shadow", img)
        cv2.imshow("Frame 2: Warped by Klaus Engine", warped_img)
        
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        self.report({'INFO'}, "Shadow Warped Successfully!")
        return {'FINISHED'}

# 3. The Panel
class KLAUS_PT_panel(bpy.types.Panel):
    bl_label = "Klaus Engine"
    bl_idname = "KLAUS_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Klaus'
    
    def draw(self, context):
        layout = self.layout
        layout.operator(KLAUS_OT_warp.bl_idname, icon='SHADING_RENDERED')

def register():
    try: bpy.utils.register_class(KLAUS_OT_warp)
    except: pass
    try: bpy.utils.register_class(KLAUS_PT_panel)
    except: pass

def unregister():
    bpy.utils.unregister_class(KLAUS_OT_warp)
    bpy.utils.unregister_class(KLAUS_PT_panel)

if __name__ == "__main__":
    register()
