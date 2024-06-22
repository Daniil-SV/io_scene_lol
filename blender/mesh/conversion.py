import bpy
import numpy as np

class DataConversions:
    inited = False
    
    @staticmethod
    def use():
        if DataConversions.inited: return
        
        if bpy.app.debug_value != 100:
            scale_factor = 1.0 / bpy.context.scene.unit_settings.scale_length
            
            def to_blender_location(array: np.ndarray):
                # x,y,z -> -x,-z,y
                array[:, [1,2]] = array[:, [2,1]]
                array[:, 1] *= -1
                #array[:, 0] *= -1
                
                # Unit conversion
                if scale_factor != 1: locs *= scale_factor
                
            def to_blender_normals(array: np.ndarray):
                array[:, [1,2]] = array[:, [2,1]]
                array[:, 1] *= -1
                #array *= -1
                
            DataConversions.to_blender_location = to_blender_location
            DataConversions.to_blender_normals = to_blender_normals
    
        DataConversions.inited = True
        
    @staticmethod
    def flip_texcoord(array: np.ndarray):
        array[:, 1] *= -1
        array[:, 1] += 1
        
    @staticmethod
    def to_blender_location(array: np.ndarray):
        return
        
    @staticmethod
    def to_blender_normals(array: np.ndarray):
        return