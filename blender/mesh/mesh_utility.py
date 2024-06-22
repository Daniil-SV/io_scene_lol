import bpy
import numpy as np
from ...logger import Logger
from .conversion import DataConversions

class MeshUtility:
    """"
        A small class with all the necessary functions for working with meshes.

        Some functions were taken directly from glTF importer and modified.
        This is in any case will be much faster and more reliable than writing completely new code for this.
    """
    
    @staticmethod
    def squish(array, dtype=None):
        """Squish nD array into a C-contiguous (required for faster access with the buffer protocol in foreach_set) 1D array
        (required by foreach_set). Optionally converting the array to a different dtype."""
        return np.ascontiguousarray(array, dtype=dtype).reshape(array.size)
    
    @staticmethod
    def create_primitive(
        name: str,
        indices: np.ndarray,
        vertices: np.ndarray,
        texcoord: np.ndarray = None
    ):
        Logger.info(f"Creating mesh with name \"{name}\", triangles: {len(indices) // 3}, UV: {texcoord is not None}")
        primitive = bpy.data.meshes.new(name)

        face_lengths = tuple(map(len, indices))
        vertices_len = len(vertices)
        faces_len = len(indices)

        primitive.vertices.add(vertices_len)
        primitive.loops.add(sum(face_lengths))
        primitive.polygons.add(faces_len)

        primitive.vertices.foreach_set("co", MeshUtility.squish(vertices))

        vertex_indices = MeshUtility.squish(indices)
        loop_starts = np.arange(0, 3 * len(indices), step=3)

        primitive.polygons.foreach_set("loop_start", loop_starts)
        primitive.polygons.foreach_set("vertices", vertex_indices)

        primitive.update(
            calc_edges=True,
            calc_edges_loose=False,
        )
        primitive.validate()
        
        if texcoord is not None:
            uv_layer = primitive.uv_layers.new(name="UVMap")
            faces_texcoord = texcoord[vertex_indices]
            DataConversions.to_blender_uv(faces_texcoord)
            
            uv_layer.data.foreach_set('uv', MeshUtility.squish(faces_texcoord))
        
        return primitive