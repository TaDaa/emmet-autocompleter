import bisect
class SortList():
    def __init__(self,iterable=(),key=None):
        if hasattr(key,'__call__'):
            self.key = key
        elif key:
            self.key = lambda x: x[key]

        sorted_list = sorted((key(value),value) for value in iterable)
        self.keys = [k for k, item in sorted_list]
        self.values = [item for k, item in sorted_list]
    def __len__(self):
        return len(self.keys)
    def remove(self,value):
        index = self.search(value)
        keys = self.keys
        target = value
        if index != -1:
            for i in range(index,len(keys)):
                if keys[i] != target:
                    break
                else:
                    del self.values[i]
                    del self.keys[i]
    def append(self,value):
        key = self.key(value)
        index = bisect.bisect_left(self.keys,key)
        self.keys.insert(index,key)
        self.values.insert(index,value)
    def appendAll(self,values):
        for value in values:
            self.append(value)
    def clear(self):
        del self.values[0:len(self.values)]
        del self.keys[0:len(self.keys)]
    def removeAll(self,values):
        key = self.key
        if isinstance(values,SortList):
            values = values.values
        for value in values:
            self.remove(value)
    def extend(self,values):
        self.sorted = False
        if isinstance(values,SortList):
            values = values.values
        for value in values:
            self.append(value)
    def reset(self):
        ln = len(self.keys)
        del self.keys[0:ln]
        del self.values[0:ln]
    def search(self,value):
        i = bisect.bisect_right(self.keys,value)
        if i:
            return i-1
        return -1
    def findRange(self,value):
        target = self.keys
        start = self.search(value)
        start_range = -1
        end_range = -1

        if len(target) == 0:
            return range(0,0)
        if len(target) <= start:
            start = len(target) - 1
        if start == -1:
            start = 0
        if target[start].startswith(value) != True:
            start += 1
        for index in range(start,len(target)):
            if (target[index].startswith(value) != True):
                index -= 1
                break
            elif start_range == -1:
                start_range = index

        if start_range != -1:
            end_range = index + 1

        return range(start_range,end_range)

        
