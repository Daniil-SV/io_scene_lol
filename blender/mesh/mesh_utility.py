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
    def set_primitive_smooth(
        mesh: bpy.types.Mesh,
        normals: np.ndarray,
        indices: np.ndarray
    ):
        num_polys = len(mesh.polygons)
        
        poly_normals = np.empty(num_polys * 3, dtype=np.float32)
        mesh.polygons.foreach_get('normal', poly_normals)
        poly_normals = poly_normals.reshape(num_polys, 3)

        # Dot product against the first vertex normal in the tri
        vert_ns = normals[indices[:3*(num_polys):3]]
        dot_prods = np.sum(vert_ns * poly_normals, axis=1)  # dot product
        smooth = (dot_prods <= 0.9999999)

        # Same for the second vertex, etc.
        vert_ns = normals[indices[1:3*(num_polys):3]]
        dot_prods = np.sum(vert_ns * poly_normals, axis=1)
        np.logical_or(smooth, dot_prods <= 0.9999999, out=smooth)

        vert_ns = normals[indices[2:3*(num_polys):3]]
        dot_prods = np.sum(vert_ns * poly_normals, axis=1)
        np.logical_or(smooth, dot_prods <= 0.9999999, out=smooth)

        mesh.polygons.foreach_set('use_smooth', smooth)
    
    @staticmethod
    def merge_primitive_vertices(
        vertices: np.ndarray,
        indices: np.ndarray,
        normals: np.ndarray = None,
    ):
        if normals is not None:
            normals *= 50000
            normals[:] = np.trunc(normals)
            normals *= (1/50000)
        
        dot_fields = [('x', np.float32), ('y', np.float32), ('z', np.float32)]
        if normals is not None:
            dot_fields += [('nx', np.float32), ('ny', np.float32), ('nz', np.float32)]

        dots = np.empty(len(vertices), dtype=np.dtype(dot_fields))
        dots['x'] = vertices[:, 0]
        dots['y'] = vertices[:, 1]
        dots['z'] = vertices[:, 2]
        
        if normals is not None:
            dots['nx'] = normals[:, 0]
            dots['ny'] = normals[:, 1]
            dots['nz'] = normals[:, 2]
            
        unique_dots, unique_ind, inv_indices = np.unique(dots, return_index=True, return_inverse=True)

        indices = inv_indices[indices]

        vertices = np.empty((len(unique_dots), 3), dtype=np.float32)
        vertices[:, 0] = unique_dots['x']
        vertices[:, 1] = unique_dots['y']
        vertices[:, 2] = unique_dots['z']
        
        if normals is not None:
            normals = np.empty((len(unique_dots), 3), dtype=np.float32)
            normals[:, 0] = unique_dots['nx']
            normals[:, 1] = unique_dots['ny']
            normals[:, 2] = unique_dots['nz']
            
        return vertices, indices, normals
    
    @staticmethod
    def create_primitive(
        name: str,
        indices: np.ndarray,
        vertices: np.ndarray,
        texcoord: np.ndarray = None,
        normals: np.ndarray = None
    ):
        Logger.info(f"Creating mesh with name \"{name}\", triangles: {len(indices) // 3}, UV: {texcoord is not None}, Normals: {normals is not None}")
        primitive = bpy.data.meshes.new(name)

        vertices, faces_indices, normals = MeshUtility.merge_primitive_vertices(
            vertices, indices, normals
        )
        
        DataConversions.use()
        DataConversions.to_blender_location(vertices)
        if normals is not None:
            DataConversions.to_blender_normals(normals)
        
        face_lengths = tuple(map(len, faces_indices))
        vertices_len = len(vertices)
        faces_len = len(faces_indices)

        primitive.vertices.add(vertices_len)
        primitive.loops.add(sum(face_lengths))
        primitive.polygons.add(faces_len)

        primitive.vertices.foreach_set("co", MeshUtility.squish(vertices))

        vertex_indices = MeshUtility.squish(faces_indices)
        loop_starts = np.arange(0, 3 * len(faces_indices), step=3)

        primitive.polygons.foreach_set("loop_start", loop_starts)
        primitive.polygons.foreach_set("vertices", vertex_indices)
        
        if texcoord is not None:
            texcoord = texcoord[MeshUtility.squish(indices)]
            DataConversions.flip_texcoord(texcoord)
            
            uv_layer = primitive.uv_layers.new(name="UVMap")
            uv_layer.data.foreach_set('uv', MeshUtility.squish(texcoord))
            
        # Not really necessary but ok
        MeshUtility.set_primitive_smooth(primitive, normals, vertex_indices)

        primitive.update(
            calc_edges=True,
            calc_edges_loose=False,
        )
        primitive.validate()

        if normals is not None:
            primitive.create_normals_split()
            primitive.normals_split_custom_set_from_vertices(normals)
            primitive.use_auto_smooth = True
        
        return primitive