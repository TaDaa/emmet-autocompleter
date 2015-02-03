#import parser.Parser as Parser
#import htmlstates.State as States

NONE = 0
NAME = 1
ATTRIBUTE = 2
VALUE = 4
MULTIPLIER = 8
TEXT = 16


class Parser():
    def __init__(self):
        self.handlers = {}
        self.buffer = ''
        self.handle('"',self.handle_double_quote)
        self.handle('\'',self.handle_single_quote)
        self.handle('<',self.handle_left_carrot)
        self.handle('>',self.handle_right_carrot)
        self.handle('^',self.handle_up_carrot)
        self.handle('+',self.handle_plus)
        self.handle('[',self.handle_start_brace)
        self.handle(']',self.handle_close_brace)
        self.handle('{',self.handle_start_bracket)
        self.handle('}',self.handle_close_bracket)
        self.handle('=',self.handle_equals)
        self.handle('*',self.handle_asterix)
        self.handle('.',self.handle_period)
        self.handle('#',self.handle_hash)
        self.handle(' ',self.handle_space)
        self.handle('\t',self.handle_tab)
    def parse(self,string,i):
        self.buffer = string
        self.stack = []
        self.match_mode = 0
        self.closed_braces = 0
        self.closed_brackets = 0
        self.double_quote_index = self.index_matching_chars('"',i)
        self.single_quote_index = self.index_matching_chars('\'',i)
        self.brace_index = self.index_open_close_chars('[',']',i)
        return self.next(i-1)
    def index_open_close_chars(self,open_ch,close_ch,column):
        buffer = self.buffer
        result = {}
        start_locations = {}
        open_count = 0
        for i in range(0,column):
            ch = buffer[i]
            if ch == open_ch:
                open_count += 1
                start_locations[open_count] = i
            elif ch == close_ch:
                if open_count in start_locations:
                    start = start_locations[open_count]
                    result[start] = result[i] = (start,i)
                    open_count -= 1
        for start in start_locations:
            result[start] = result[column] = (start,column)
        return result
    def index_matching_chars(self,target,column):
        buffer = self.buffer
        result = {}
        start_locations = {}
        escape_count = 0
        for i in range(0,column):
            ch = buffer[i]
            if ch == '\\':
                escape_count += 1
            elif ch == target:
                if not escape_count in start_locations:
                    start_locations[escape_count] = i
                else:
                    start = start_locations[escape_count]
                    result[start] = result[i] = (start,i)
                    del start_locations[escape_count]
                escape_count = 0
            else:
                escape_count = 0
        for level in start_locations:
            start = start_locations[level]
            result[start] = result[column+1] = (start,column+1)
        return result
    def handle(self,char,func):
        if not char in self.handlers:
            self.handlers[char] = func
    def handle_equals(self,word,i):
        #if len(self.stack > 1):
            #if self.stack[1][0] == '"' or self.stack[1][0] == '\'':
                #return (VALUE)
            #else:
        state = self.next(i-1)
        if state[0] == ATTRIBUTE:
            return (VALUE,state[1],state[2],word)
        return False
    def handle_start_brace(self,word,i):
        #if we encounter a start brace -- need to go backwards until tagstart -- 
        #gets tricky...suppose we encounter }, needs to terminate, encounter non-matching start '[' , needs to terminate
        #encounter text after end brace needs to terminate
        if self.match_mode == 0:
            self.match_mode = 1
        else:
            self.closed_braces -= 1
            if self.closed_braces != 0:
                return (NAME,word)

        state = self.next(i-1)
        return (ATTRIBUTE,state[1],word)
    def handle_start_bracket(self,word,i):
        if self.match_mode == 0:
            self.match_mode = 1
        else:
            return (NAME,word)
        state = self.next(i-1)
        return (TEXT,state[1],word)
    def handle_close_bracket(self,word,i):
        return self.handle_tag_break(word,i)
    def handle_double_quote(self,word,i):
        return self.handle_quote(self.double_quote_index,word,i)
    def handle_single_quote(self,word,i):
        return self.handle_quote(self.single_quote_index,word,i)
    def handle_quote(self,lookup,word,i):
        if i in lookup:
            index = lookup[i][0]
            state = self.next(index-1)
            if state[0] == ATTRIBUTE:
                return (ATTRIBUTE,state[1],word)
                #return state[0:len(state)-1] + tuple([word])
            elif state[0] == VALUE:
                if i == lookup[i][1]:
                    return (ATTRIBUTE,state[1],word)
                elif state[3] == '':
                    return (VALUE,state[1],state[2],word)
                return state
            else:
                return (NAME,word)
    def handle_close_brace(self,word,i):
        if len(word) > 0 or len(self.stack) == 1:
            return (NAME,word)
        else:
            buffer= self.buffer
            lookup = self.brace_index
            index = i
            if i in lookup:
                index = lookup[i][0]
            state = self.next(index-1)
            return (ATTRIBUTE,state[1],word)
            #skip to matching brace
        return
    def handle_plus(self,word,i):
        return self.handle_tag_break(word,i)
    def handle_left_carrot(self,word,i):
        if len(self.stack) > 1:
            ch = self.stack[-2][0]
            if ch == ' ' or ch == '\t':
                attr = False
                for j in range(len(self.stack)-2,-1,-1):
                    ch = self.stack[j][0]
                    if ch != ' ' and ch != '\t':
                        break
                    else:
                        attr = self.stack[j][1]
                if attr != False:
                    return (ATTRIBUTE,word,attr)
        return self.handle_tag_break(word,i)
    def handle_up_carrot(self,word,i):
        return self.handle_tag_break(word,i)
    def handle_right_carrot(self,word,i):
        return self.handle_tag_break(word,i)
    def handle_tag_break(self,word,i):
        return (NAME,word)
    def handle_asterix(self,word,i):
        valid = len(self.stack) == 1
        if valid:
            state = self.next(i-1)
        mult = ''
        z = -1
        for j in range(0,len(word)):
            ch = word[j]
            if ch < '0' or ch > '9':
                valid = False
                break
            else:
                z += 1
                mult += ch
        if valid == False:
            return (NAME,word[z+1:len(word)])
        return (MULTIPLIER,state[1],mult)
    def handle_blank (self,word,i):
        state = self.next(i-1)
        if state[0] == VALUE:
            return (ATTRIBUTE,state[1],word)
        return state[0:len(state)-1] + tuple([word])
    def handle_space(self,word,i):
        return self.handle_blank(word,i)
    def handle_tab(self,word,i):
        return self.handle_blank(word,i)
        #return False #words go on stack
    def handle_period(self,word,i):
        state = self.next(i-1)
        return (VALUE,state[1],'className',word)
    def handle_hash(self,word,i):
        state = self.next(i-1)
        return (VALUE,state[1],'id',word)
    def next(self,column):
        buffer = self.buffer
        handlers = self.handlers
        word = ''
        state = False 
        for i in range(column,-1,-1):
            ch = buffer[i]
            if ch in handlers:
                self.stack.append((ch,word))
                state = handlers[ch](word,i)
                word = ''
                if state != False:
                    break
            else:
                word = ch + word


        if state == False:
            return (NAME,word)

        #if state[0] == ATTRIBUTE and self.stack[0][0] == ' ' or self.stack[0][1] == '\t':
            #return state[0:len(state)-1] + tuple([self.stack[0][1]])
        return state

