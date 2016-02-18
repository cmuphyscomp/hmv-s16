"""\
ghutil.trees

Utility functions related to creating Data Trees in Grasshopper.
"""

# import the Grasshopper Data Tree API
import Grasshopper as gh

#================================================================
# from https://gist.github.com/piac/ef91ac83cb5ee92a1294
def list_to_tree(input, none_and_holes=True, source=[0]):
    """Transforms nestings of lists or tuples to a Grasshopper DataTree"""
    from Grasshopper import DataTree as Tree
    from Grasshopper.Kernel.Data import GH_Path as Path
    from System import Array
    def proc(input,tree,track):
        path = Path(Array[int](track))
        if len(input) == 0 and none_and_holes: tree.EnsurePath(path); return
        for i,item in enumerate(input):
            if hasattr(item, '__iter__'): #if list or tuple
                track.append(i); proc(item,tree,track); track.pop()
            else:
                if none_and_holes: tree.Insert(item,path,i)
                elif item is not None: tree.Add(item,path)
    if input is not None: t=Tree[object]();proc(input,t,source[:]);return t

#================================================================
def vectors_to_data_tree(vector_list):
    """Convert a list of Python tuples of floats to a GH datatree."""
    dataTree = gh.DataTree[float]()
    for i,vec in enumerate(vector_list):
        for value in vec:
            dataTree.Add(value,gh.Kernel.Data.GH_Path(i))
    return dataTree

#================================================================
