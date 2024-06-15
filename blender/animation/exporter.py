import bpy
from bpy.props import (StringProperty,
                        IntProperty)
from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper
from ...logger import Logger
from ...resources.animation import AnimationAsset
from ...resources.animation.transform_storage import TransformStorage
from mathutils import Vector, Quaternion

class AnimationExporter(Operator, ExportHelper):
    bl_idname = "export_scene.lol_animation"
    bl_label = "LoL Animation"
    bl_description = "Export animation from selected skeleton to .ANM file"
    bl_options = { 'PRESET' }

    filename_ext = '.anm'

    filter_glob: StringProperty(default=f'*{filename_ext}', options={ 'HIDDEN' })

    #compress: BoolProperty(
    #    name='Compress animation asset',
    #    description='',
    #    default=True
    #)

    #quantize: BoolProperty(
    #    name='Quantize Rotation',
    #    description='',
    #    default=True
    #)
    
    transform_tolerance: IntProperty(
        name="Transform Tolerance", 
        description="Tolerence of Scale and Translation", 
        default=70,
        min=0,
        max=100,
        subtype="FACTOR"
    )
    
    rotation_tolerance: IntProperty(
        name="Rotation Tolerance", 
        description="Tolerance of Rotation", 
        default=60,
        min=0,
        max=100,
        subtype="FACTOR"
    )

    def __init__(self) -> None:
        pass

    def execute(self, context: bpy.types.Context):
        Logger.execute(__name__)
        
        TransformStorage.TransformTolerance = (100 - self.transform_tolerance) / 1000
        TransformStorage.RotationTolerance = (100 - self.rotation_tolerance) / 10000
        
        self.export_animation(context)
        Logger.final()
        
        self.report({"INFO"}, "Done")
        return{ 'FINISHED' }
    
    def export_animation(self, context: bpy.types.Context) -> None:
        Logger.info(f"Exporting {self.filepath}")

        objects = context.selected_objects
        if (len(objects) == 0):
            self.report({'ERROR'}, "Select any skeleton object before exporting")
            return

        object: bpy.types.Object = objects[0]
        if (object.type != "ARMATURE"):
            self.report({'ERROR'}, "Selected object is not armature") 
            return
        
        self.write_uncompressed_animation(context, object)

    def write_uncompressed_animation(self, context: bpy.types.Context, object: bpy.types.Object):
        joints = object.animation_data.action.groups
        keyframes = [int(keyframe.co.x) for fcurve in object.animation_data.action.fcurves for keyframe in fcurve.keyframe_points]

        first_frame = min(keyframes)
        last_frame = max(keyframes) + 1
        frame_count = last_frame - first_frame
        Logger.info(f"Start Frame - {first_frame}; End Frame - {last_frame}; Frame Count - {frame_count}")

        asset = AnimationAsset()
        asset.fps = context.scene.render.fps / context.scene.render.fps_base
        asset.duration = frame_count
        asset.joints = [joint.name for joint in joints]
        asset.storage.indices_from_count(frame_count, len(joints))
        
        # Step 1. Gathering all transforms to local bank for each joint
        joints_transforms = [TransformStorage() for _ in range(len(joints))] 
        for transform in joints_transforms:
            transform.indices_from_count(frame_count, 1)
        
        for i in range(frame_count):
            Logger.progress("Step 1. Current frame", i, ((frame_count - 1 ) == i))

            context.scene.frame_set(first_frame + i)
            context.view_layer.update()

            for t in range(len(joints)):
                bone: bpy.types.PoseBone = object.pose.bones.get(joints[t].name)
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
        for i in range(frame_count):
            Logger.progress("Step 2. Current frame", i, ((frame_count - 1 ) == i))
            
            for t in range(len(joints)):
                packed_rotations = joints_packed_rotations[t]
                packed_transforms = joints_packed_transforms[t]
                storage = joints_transforms[t]

                # Frame transforms
                translation, scale, rotation = storage.indices[i]
                
                elements_offset = (len(joints) * i) + t
                if (translation in packed_transforms):
                    asset.storage.set_translation_index(packed_transforms[translation], elements_offset)
                else:
                    translation_index = asset.storage.set_translation_approx(storage.transforms[translation], elements_offset)
                    packed_transforms[translation] = translation_index
                    
                if (scale in packed_transforms):
                    asset.storage.set_scale_index(packed_transforms[scale], elements_offset)
                else:
                    scale_index = asset.storage.set_scale_approx(storage.transforms[scale], elements_offset)
                    packed_transforms[scale] = scale_index
                    
                if (rotation in packed_rotations):
                    asset.storage.set_rotation_index(packed_rotations[rotation], elements_offset)
                else:
                    rotation_index = asset.storage.set_rotation_approx(storage.rotations[rotation], elements_offset)
                    packed_rotations[rotation] = rotation_index
            
            
        data = asset.write()
        with open(self.filepath, "wb") as file:
            file.write(data)
