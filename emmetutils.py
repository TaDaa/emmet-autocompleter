from os import walk,path
import bisect

folder = {}

def getProjectFiles(project,excluded_names):
    result = []
    for (dir_path,dir_names,files) in walk(project):
        [(result.append(File(path.join(dir_path,f).replace('\\','/'),True))) for f in files]
    if excluded_names:
        for f in result:
            if f.path in excluded_names:
                result.remove(f)
    return result

class File():
    def __init__(self,p,mtime=False):
        split = path.splitext(p)
        self.name = path.basename(split[0])
        self.path = p
        self.extension = split[1]
        if mtime:
            self.modified = path.getmtime(p)
        self.removed = False


def byteify(input):
    if isinstance(input, dict):
        return {byteify(key):byteify(value) for key,value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input

def getModifiedFiles(project,extensions,excluded_names):
    global folder
    if not project in folder:
        folder[project] = {}
    active_folder = folder[project]
    active_keys = active_folder.keys()
    files = getProjectFiles(project,excluded_names)
    for f in files:
        path = f.path
        if path in active_folder:
            active_keys.remove(path)
        if not path in active_folder or f.modified > active_folder[path].modified:
            if extensions != None and f.extension not in extensions:
                files.remove(f)
            else:
                active_folder[path] = f


    for path in active_keys:
        f = active_folder[path]
        files.append(f)
        del active_folder[path]
        f.removed = True
    return files
