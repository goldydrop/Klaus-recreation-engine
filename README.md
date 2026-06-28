Klaus Engine - Project Roadmap & Status

Project: Klaus Engine (True TPS Shadow Warper)
1. What I Am Making:
A Blender animation tool/add-on that uses Thin Plate Spline (TPS) interpolation via OpenCV to automatically warp and deform a 2D shadow texture based on the movement of hand-drawn Grease Pencil keyframes.

2. Where I Am At (Current Status)
• Dependency Injection: 100% Successful. We successfully bypassed Blender 5.0's isolated environment using a priority path override (`sys.path.insert(0)`), allowing the script to load external `cv2` (OpenCV) and `numpy` math libraries flawlessly.

• Point Resampling: 100% Successful. Built a bulletproof stroke resampler (`resample_stroke` and `get_vec`) capable of processing both raw math vectors and stroke point objects uniformly.

• The Current Roadblock: We ran directly into Blender's new Grease Pencil v3 architectural overhaul. The script threw an `AttributeError: 'GreasePencil' object has no attribute 'layers'`. This means the old way of accessing drawing frames and strokes has changed in Blender 5.0.

3. Where We Are Headed (Next Steps)
1. Update Grease Pencil API Syntax: Modify the layer, frame, and stroke fetching logic to conform with the new Blender 5.0 Grease Pencil v3 data structure (navigating the new geometry/drawing blocks instead of the legacy `.layers`).

2. 2D/3D Coordinate Projection: Perfect the scaling and transformation variables so that the 3D viewport stroke coordinates map precisely to the 2D pixel space used by the Thin Plate Spline transformer.

3. Internal Texture Baking: Replace the temporary testing windows (`cv2.imshow`) with a pipeline that bakes the warped shadow directly back into an internal Blender image texture.
