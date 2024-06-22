
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

def cleanup_module():
    import sys

    all_modules = sys.modules
    all_modules = dict(sorted(all_modules.items(),key= lambda x:x[0]))

    for m in all_modules:
        if m.startswith(__name__):
            del sys.modules[m]

import bpy
from bpy.types import Operator
from .operators import *

classes = [
    AnimationExporter,
    SkinnedMeshImporter
]

importers = \
[
    SkinnedMeshImporter
]

exporters = \
[
    AnimationExporter
]

classes = importers + exporters

def make_operator(operator: Operator):
    def func(self, _):
        self.layout.operator(operator.bl_idname, text=f'{operator.bl_label} ({operator.filename_ext})')
    return func


def register():
    for c in classes:
        bpy.utils.register_class(c)
    
    for c in importers:
        bpy.types.TOPBAR_MT_file_import.append(make_operator(c))
        
    for c in exporters:
        bpy.types.TOPBAR_MT_file_export.append(make_operator(c))

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)

    for c in importers:
        bpy.types.TOPBAR_MT_file_import.remove(make_operator(c))
        
    for c in exporters:
        bpy.types.TOPBAR_MT_file_export.remove(make_operator(c))
        
    cleanup_module()

if __name__ == "__main__":
    register()
