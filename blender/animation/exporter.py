import bpy
from ...logger import Logger
from ...resources.animation import AnimationAsset
from ...resources.animation.transform_storage import TransformStorage
from mathutils import Vector, Quaternion

class LolSceneAnimationExportSettings:
    def __init__(self) -> None:
        self.output_path: str = None
        self.compressed: bool = None
        self.transform_tolerance: int = None
        self.rotation_tolerance: int = None

class LolSceneAnimationExporter:
    def __init__(self, context: bpy.types.Context, object: bpy.types.Object, config: LolSceneAnimationExportSettings) -> None:
        self.object = object
        
        if config.compressed:
            raise NotImplementedError()
            
        TransformStorage.TransformTolerance = (100 - config.transform_tolerance) / 1000
        TransformStorage.RotationTolerance = (100 - config.rotation_tolerance) / 10000
        
        Logger.info(f"Exporting Animation Asset to \"{config.output_path}\"")
        
        keyframes = [int(keyframe.co.x) for fcurve in object.animation_data.action.fcurves for keyframe in fcurve.keyframe_points]
        first_frame = min(keyframes)
        last_frame = max(keyframes) + 1
        frame_count = last_frame - first_frame
        Logger.info(f"Start Frame - {first_frame}; End Frame - {last_frame}; Frame Count - {frame_count}")
        
        self.asset = AnimationAsset()
        self.asset.fps = context.scene.render.fps / context.scene.render.fps_base
        self.asset.duration = frame_count
        
        
    def export_uncompressed(self, context: bpy.types.Context):
        joints = self.object.animation_data.action.groups
        self.asset.joints = [joint.name for joint in joints]
        self.asset.storage.indices_from_count(self.asset.duration, len(joints))
        
        # Step 1. Gathering all transforms to local bank for each joint
        joints_transforms = [TransformStorage() for _ in range(len(joints))] 
        for transform in joints_transforms:
            transform.indices_from_count(self.asset.duration, 1)
        
        for i in range(self.asset.duration):
            Logger.progress("Step 1. Current frame", i, ((self.asset.duration - 1 ) == i))

            context.scene.frame_set(self.asset.duration + i)
            context.view_layer.update()

            for t in range(len(joints)):
                bone: bpy.types.PoseBone = self.object.pose.bones.get(joints[t].name)
                transform_matrix = bone.matrix

                if bone.parent:
                    transform_matrix = bone.parent.matrix.inverted() @ transform_matrix

                scale: Vector = transform_matrix.to_scale()
                translation: Vector = transform_matrix.to_translation()
                rotation: Quaternion = transform_matrix.to_quaternion() 

                if bone.parent is None:
                    rotation = bone.matrix_basis.to_quaternion()
                    rotation.x *= -1
                    rotation.y *= -1
                    rotation = Quaternion((rotation.y, rotation.z, rotation.w, rotation.x ))
                    translation = Vector((translation.x, translation.z, -translation.y))
                
                bank = joints_transforms[t]
                bank.set_translation_rough(translation, i)
                bank.set_scale_rough(scale, i)
                bank.set_rotation_rough(rotation, i)

        # Step 2. Packing all transforms to one big bank in asset
        joints_packed_transforms: list[dict[int, int]] = [{} for _ in range(len(joints))]
        joints_packed_rotations: list[dict[int, int]] = [{} for _ in range(len(joints))]
        for i in range(self.asset.duration):
            Logger.progress("Step 2. Current frame", i, ((self.asset.duration - 1 ) == i))
            
            for t in range(len(joints)):
                packed_rotations = joints_packed_rotations[t]
                packed_transforms = joints_packed_transforms[t]
                storage = joints_transforms[t]

                # Frame transforms
                translation, scale, rotation = storage.indices[i]
                
                elements_offset = (len(joints) * i) + t
                if (translation in packed_transforms):
                    self.asset.storage.set_translation_index(packed_transforms[translation], elements_offset)
                else:
                    translation_index = self.asset.storage.set_translation_approx(storage.transforms[translation], elements_offset)
                    packed_transforms[translation] = translation_index
                    
                if (scale in packed_transforms):
                    self.asset.storage.set_scale_index(packed_transforms[scale], elements_offset)
                else:
                    scale_index = self.asset.storage.set_scale_approx(storage.transforms[scale], elements_offset)
                    packed_transforms[scale] = scale_index
                    
                if (rotation in packed_rotations):
                    self.asset.storage.set_rotation_index(packed_rotations[rotation], elements_offset)
                else:
                    rotation_index = self.asset.storage.set_rotation_approx(storage.rotations[rotation], elements_offset)
                    packed_rotations[rotation] = rotation_index
    
    def export(self, context: bpy.types.Context) -> None:
        self.export_uncompressed(context)

        data = self.asset.write()
        with open(self.config.output_path, "wb") as file:
            file.write(data)