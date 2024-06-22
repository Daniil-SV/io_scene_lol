import bpy
import numpy as np
from pathlib import Path
from ...resources.skeleton import SkeletonAsset
from ...resources.skinned_mesh import SkinnedMeshAsset
from ..mesh.mesh_utility import MeshUtility

class LolSceneSkinnedImportSettings:
    def __init__(self) -> None:
        self.skeleton_filepath: str = None
        self.skin_filepath: str = None

class LolSceneSkinnedImport:
    def __init__(self, config: LolSceneSkinnedImportSettings) -> None:
        self.name = Path(config.skin_filepath).stem
        self.asset = SkinnedMeshAsset()
        self.asset.read(config.skin_filepath)
        self.skeleton: SkeletonAsset  = None
        
        if config.skeleton_filepath is not None:
            self.skeleton = SkeletonAsset()
            self.skeleton.read(config.skeleton_filepath)

    def import_primitive(self, context: bpy.types.Context) -> list[bpy.types.Mesh]:
        vertices = self.asset.vertices
        indices = self.asset.indices
        primitive = MeshUtility.create_primitive(
            f"{self.name}-mesh",
            self.asset.materials,
            indices,
            vertices,
            texcoord=self.asset.texcoord,
            normals=self.asset.normals
        )
        
        return [bpy.data.objects.new(self.name, primitive)]
    
    def import_scene(self, context: bpy.types.Context) -> None:
        objects = self.import_primitive(context)
        
        for mesh in objects:
            context.scene.collection.objects.link(mesh)