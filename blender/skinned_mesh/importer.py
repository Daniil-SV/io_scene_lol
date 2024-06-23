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
        self.split_materials: bool = None

class LolSceneSkinnedImport:
    def __init__(self, config: LolSceneSkinnedImportSettings) -> None:
        self.name = Path(config.skin_filepath).stem
        self.asset = SkinnedMeshAsset()
        self.asset.read(config.skin_filepath)
        self.skeleton: SkeletonAsset  = None
        self.split_materials = config.split_materials
        
        if config.skeleton_filepath is not None:
            self.skeleton = SkeletonAsset()
            self.skeleton.read(config.skeleton_filepath)

    def import_primitive(self, context: bpy.types.Context) -> list[bpy.types.Mesh]:
        if not self.split_materials:
            primitive = MeshUtility.create_primitive(
                f"{self.name}-mesh",
                self.asset.materials,
                self.asset.indices,
                self.asset.vertices,
                texcoord=self.asset.texcoord,
                normals=self.asset.normals
            )
            
            return [bpy.data.objects.new(self.name, primitive)]
        
        objects: list[bpy.types.Mesh] = []
        for material in self.asset.materials:
            material_object_name = f"{self.name}_{material.name}"
            material_object = self.asset.from_material(material)
            
            primitive = MeshUtility.create_primitive(
                f"{material_object_name}-mesh",
                material_object.materials,
                material_object.indices,
                material_object.vertices,
                texcoord=material_object.texcoord,
                normals=material_object.normals
            )
            objects.append(
                bpy.data.objects.new(material_object_name, primitive)
            )
            
        return objects
    
    def import_scene(self, context: bpy.types.Context) -> None:
        objects = self.import_primitive(context)
        
        for mesh in objects:
            context.scene.collection.objects.link(mesh)