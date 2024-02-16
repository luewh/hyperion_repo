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

prefix = "_convexHull"
ms = pymeshlab.MeshSet()
for path in paths:

    ms.load_new_mesh(path)

    ms.generate_convex_hull()
    

    fileName = path.split('\\')[-1]
    print(fileName)
    ms.save_current_mesh(fileName[:-4]+prefix+'.stl')


