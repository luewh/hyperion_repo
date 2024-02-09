import pymeshlab
from os import walk

def getPaths(path="./"):
    paths = []
    for root, _, files in walk(path):
        for file in files:
            if file[-4:].lower() == ".stl":
                paths.append(root+'\\'+file)
    return paths

paths = getPaths()

# pymeshlab.print_filter_list()
# pymeshlab.print_filter_parameter_list('meshing_merge_close_vertices')

pourcentage = 2
prefix = "_optimized"
ms = pymeshlab.MeshSet()
for path in paths:

    ms.load_new_mesh(path)

    ms.meshing_remove_duplicate_faces()
    ms.meshing_remove_null_faces()
    ms.meshing_remove_duplicate_vertices()
    ms.meshing_remove_unreferenced_vertices()
    
    ms.meshing_merge_close_vertices(
        threshold=pymeshlab.pmeshlab.Percentage(pourcentage))
    
    ms.meshing_remove_duplicate_faces()
    ms.meshing_remove_null_faces()
    ms.meshing_remove_duplicate_vertices()
    ms.meshing_remove_unreferenced_vertices()

    ms.meshing_repair_non_manifold_edges()

    ms.meshing_remove_duplicate_faces()
    ms.meshing_remove_null_faces()
    ms.meshing_remove_duplicate_vertices()
    ms.meshing_remove_unreferenced_vertices()

    ms.meshing_decimation_quadric_edge_collapse(
        preserveboundary=True,
        preservenormal=True,
        preservetopology=True,
        optimalplacement=True)
    
    ms.meshing_remove_duplicate_faces()
    ms.meshing_remove_null_faces()
    ms.meshing_remove_duplicate_vertices()
    ms.meshing_remove_unreferenced_vertices()

    ms.meshing_merge_close_vertices(
        threshold=pymeshlab.pmeshlab.Percentage(pourcentage))
    
    ms.meshing_remove_duplicate_faces()
    ms.meshing_remove_null_faces()
    ms.meshing_remove_duplicate_vertices()
    ms.meshing_remove_unreferenced_vertices()

    ms.meshing_repair_non_manifold_edges()

    ms.meshing_remove_duplicate_faces()
    ms.meshing_remove_null_faces()
    ms.meshing_remove_duplicate_vertices()
    ms.meshing_remove_unreferenced_vertices()

    fileName = path.split('\\')[-1]
    print(fileName)
    ms.save_current_mesh(fileName[:-4]+prefix+'.stl')


