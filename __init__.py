
bl_info = {
    "name": "League Of Legends Formats Addon",
    "description": "Importer and exporter for League of Legends 3D assets",
    "author": "DaniilSV",
    "version": (1, 0),
    "support": "COMMUNITY",
    "blender": (3, 4, 0),
    "location": "File > Import-Export",
    "category": "Import-Export"
}

def reload_package(module_dict_main):
    import importlib
    from pathlib import Path

    def reload_package_recursive(current_dir, module_dict):
        for path in current_dir.iterdir():
            if "__init__" in str(path) or path.stem not in module_dict:
                continue

            if path.is_file() and path.suffix == ".py":
                importlib.reload(module_dict[path.stem])
            elif path.is_dir():
                reload_package_recursive(path, module_dict[path.stem].__dict__)

    reload_package_recursive(Path(__file__).parent, module_dict_main)


if "bpy" in locals():
    reload_package(locals())

import bpy
from bpy.types import Operator
from .blender import *

classes = [
    AnimationExporter,
    SkinnedMeshImporter
]

def make_operator(operator: Operator):
    def func(self, _):
        self.layout.operator(operator.bl_idname, text=f'{operator.bl_label} ({operator.filename_ext})')
    return func



def register():
    for c in classes:
        bpy.utils.register_class(c)
        
    bpy.types.TOPBAR_MT_file_import.append(make_operator(SkinnedMeshImporter))
    
    bpy.types.TOPBAR_MT_file_export.append(make_operator(AnimationExporter))

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)

    bpy.types.TOPBAR_MT_file_import.remove(make_operator(SkinnedMeshImporter))
    bpy.types.TOPBAR_MT_file_export.remove(make_operator(AnimationExporter))

if __name__ == "__main__":
    register()
