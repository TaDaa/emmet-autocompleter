import sortlist, emmetparser,json
import emmetutils as utils

_reuse_map = {}
_lambda_name_getter = lambda x: x['name']


def factory():
    def _reuse_completions(tags):
        global _reuse_map
        for tag in tags:
            tag_value = tags[tag]
            if not 'name' in tag_value:
                tag_value['name'] = tag
            if 'attributes' in tag_value:
                attributes = tag_value['attributes']
                attribute_ids = [(json.dumps(attributes)) for attribute in attributes]
                attribute_keys = attributes.keys()
                joined_attribute = ''.join(attribute_ids)
                if not joined_attribute in _reuse_map:
                    for key in attribute_keys:
                        attribute = attributes[key]
                        attribute['name'] = key
                        if 'values' in attribute:
                            values = attribute['values']
                            for i in range(0,len(values)):
                                value = values[i]
                                if isinstance(value,str):
                                    values[i] = {"name":value}
                            value_ids = [(json.dumps(value)) for value in values]
                            joined_value = ''.join(value_ids)
                            if not joined_value in _reuse_map:
                                values = sortlist.SortList(values,_lambda_name_getter)
                                _reuse_map[joined_value] = values
                            attribute['values'] = _reuse_map[joined_value]
                    _reuse_map[joined_attribute] = sortlist.SortList(attributes.values(),_lambda_name_getter)
                tag_value['attributes'] = _reuse_map[joined_attribute]


    class Completer():
        def __init__(self):
            self.events = {"complete":[]}
            self.symbols = {}
            self.types = {}
            self.emmet_parser = emmetparser.Parser()
            return
        def readCompletionsFromFile(self,file):
            result = ''
            with open(file) as f:
                result = utils.byteify(json.loads(f.read()))
            _reuse_completions(result)
            return result.values()
        def addSymbols(self,type,symbols):
            if not type in self.symbols:
                self.symbols[type] = symbols
        def addSymbolsFromFile(self,type,file):
            completions = self.readCompletionsFromFile(file)
            if not type in self.symbols:
                self.symbols[type] = sortlist.SortList(completions,_lambda_name_getter)
            else:
                self.symbols[type].extend(completions)
        def findExact(self,sortlist,target):
            index = sortlist.search(target)
            if index != -1 and len(sortlist):
                if sortlist.keys[index] == target:
                    return sortlist.values[index]
            return None
        def findCompletions(self,sortlist,target,menu=None,results={}):
            range_value = sortlist.findRange(target)
            keys  = sortlist.keys
            result = []
            if len(keys):
                if menu != None:
                    for i in range_value:
                        key = keys[i]
                        if not key in results:
                            results[key] = {"abbr":keys[i],"icase":1,"dup":1,"word":keys[i],"menu":menu}
                            result.append(results[key])
                        else:
                            results[key]["menu"] += '|'+menu
                else:
                    for i in range_value:
                        if not key in results:
                            results[key] = {"abbr":keys[i],"icase":1,"dup":1,"word":keys[i]}
                            result.append(results[key])
            return result
        def on(self,name,fn):
            if name in self.events:
                self.events[name].append(fn)
            else:
                self.events[name] = [fn]
        def filter(self,target=None,func=None):
            symbols = self.symbols
            if func:
                if not target:
                    for symbol in symbols:
                        func(symbol,symbols[symbol])
                else:
                    for symbol in target:
                        if symbol in symbols:
                            func(symbol,symbols[symbol])
        def handleType(self,type,symbolNames=None):
            if symbolNames == None:
                del self.types[type]
            else:
                self.types[type] = symbolNames
        def getCompletions(self,line,column,project,type,name,buffer):
                active_line = buffer[line]

                if type in self.types:
                    filter = self.types[type]
                else:
                    filter = None

                for type in filter:
                    if type in self.events:
                        for func in self.events[type]:
                            func(self,line,column,project,type,name,buffer)
                state = self.emmet_parser.parse(active_line,column)
                symbols = self.symbols
                result = []
                result_map = {}
                target = ''
                type = state[0]
                tag = state[1]

                if type == emmetparser.MULTIPLIER:
                    tag = ''
                if type == emmetparser.NAME or type == emmetparser.MULTIPLIER:
                    target = tag
                    self.filter(filter,lambda key,value: result.extend(self.findCompletions(sortlist=value,target=target,menu=key,results=result_map)))
                else:
                    matches = []
                    self.filter(filter,lambda key,value:matches.append((key,self.findExact(value,tag))))
                    if type == emmetparser.ATTRIBUTE:
                        target = state[2]
                        for match in matches:
                            if match[1] != None:
                                result.extend(self.findCompletions(sortlist=match[1]['attributes'],target=target,menu=match[0],results=result_map))
                return {'words' : result, 'column_start':column-len(target)}


    return Completer()


completer = factory()


handleType = completer.handleType
addSymbols = completer.addSymbols
addSymbolsFromFile = completer.addSymbolsFromFile
getCompletions = completer.getCompletions
on = completer.on

del factory
