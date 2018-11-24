import emmetutils as utils
import emmetparser as parser
import emmetcompleter as completer
import imp

addSymbolsFromFile = completer.addSymbolsFromFile
handleType = completer.handleType
getCompletions = completer.getCompletions

def runScript(name,script):
    mod = imp.load_source(name,script)
    if mod.run:
        mod.run(completer)
