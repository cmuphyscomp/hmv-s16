# SortedPaths.py - contents of the ghpython object
# inputs
#  names - list of body names from a mocap stream

# outputs
#  paths - list of data tree paths in order sorted by name
#  Pn    - individual path

sorted_names = sorted(names)
indices = [names.index(name) for name in sorted_names]
paths = ["0;%d" % index for index in indices]

p1 = paths[0]
p2 = paths[1]
p3 = paths[2]
