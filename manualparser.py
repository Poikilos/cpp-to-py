class ACls:
    def __init__(self):
        self.name = None

class AVar:
    def __init__(self):
        self._cls = None
        self._t = None
        self._st = None

class AScope:
    '''
    Members:
    _vars: variables (of type AVar)
    _
    '''
    def __init__(self):
        self._vars = {}
        self._clss = {}

class ManualParser:
    '''
    Members:
    multis['cao']: a plain list of compound assignment operators derived
                  from openers['cao'] (double-character or more)
    multis['co']: a plain list of comparison operators derived
                 from openers['co'] (double-character or more)
    multis['lo']: a plain list of logical operators derived
                 from openers['lo'] (double-character or more)
    multis['bua']: a plain list of bidirectional unary operators derived
                  from openers['bua'] (double-character)
    multis['sa']: a plain list of scope operators derived
                  from openers['sa'] (double-character)
    pysigns: a dictionary of operators mapped to
             the python equivalent (the value)
    '''
    def __init__(self):
        self.scopes = []
        self.globalScopeCount = 0;
        self.showAll = False
        self.fromLang = "CPP"
        '''
        coaOpeners: compound assignment operators where the key is the
                    second character and the value is a list of openers
        '''
        openers = {}

        openers['ca'] = {}
        openers['ca']['='] = ['!', '=', '>', '<']

        openers['lo'] = {}
        openers['lo']['&'] = ['&']
        openers['lo']['|'] = ['|']
        openers['lo']['<'] = ['<']

        openers['cao'] = {}
        openers['cao']['='] = ['+', '-', '*', '/', '%',
                               '>>', '<<', '&', '^', '|']

        openers['bua'] = {}
        openers['bua']['+'] = ['+']
        openers['bua']['-'] = ['-']

        openers['sa'] = {}
        openers['sa'][':'] = [':']
        openers['sa']['>'] = ['-']

        self.multis = {}
        for key, openerDict in openers.items():
            self.multis[key] = []
            for closer, openerList in openerDict.items():
                for opener in openerList:
                    # sys.stderr.write("* adding {} to {}\n"
                    #                  "".format(opener+closer, key))
                    # ^ such as: "* adding <<= to cao"
                    # ^ such as: "* adding -- to bua"
                    self.multis[key].append(opener+closer)
        self.pysigns = {}
        self.pysigns['!'] = 'not '
        self.pysigns['&&'] = " and "
        self.pysigns['||'] = " or "
        # ^ The above changes are necessary because
        #   evalexpr_string in the example parser doesn't actually
        #   make these changes. It only generates Python code
        #   temporarily for the purpose of running eval to run
        #   preprocessor macros.
        self.pysigns['++'] = " += 1"
        self.pysigns['--'] = " -= 1"
        self.pysigns['::'] = "."
        self.pysigns['->'] = "."
        self.pysigns['&'] = '(AND)'
        self.pysigns['|'] = '(OR)'
        self.pysigns['^'] = '(XOR)'
        self.pysigns['~'] = '(NOT)'
        self.pysigns['<<'] = '(SHIFTL)'
        self.pysigns['>>'] = '(SHIFTR)'
        self.pysigns['new'] = ''
        # TODO: handle casts (c-style and STL)
        # TODO: handle ?: (ternary operator)
        # TODO: handle & (reference)
        # TODO: handle * (dereference)
        # self.buffer = ""
        self.path = None
        # self._line = ""
        self._parts = []
        self._lines = []

    '''
    def flush(self):
        if len(self.buffer) > 0:
            sys.stdout.write(self.buffer)
        sys.stdout.flush()
    '''

    def fromTokens(self, p):
        '''
        Sequential arguments:
        p - a Preprocessor such as from ply/cpp.py
        '''
        if len(self.scopes) > 1:
            raise RuntimeError("When parsing a new file, the scope"
                               " shouldn't already be deeper than the"
                               " global scope.")
        elif len(self.scopes) < 1:
            if (self.globalScopeCount > 0):
                raise RuntimeError("There was already a global scope"
                                   " but it was missing or deleted"
                                   " (It should only be created once"
                                   " per program).")
            sys.stderr.write("* starting a new global scope\n")
            self.scopes.append(Scope())
            # ^ the global scope should always be active.
            self.globalScopeCount += 1
        program = self
        collect = self.collect
        while True:
            tok = p.token()
            if not tok: break
            # print(p.source, tok)
            # ^ example:
            #   "mainwindow.cpp LexToken(CPP_WS,'\n',1169,66730)"
            #   WS: whitespace
            # print(dir(tok))
            # ^ has:
            # - lexpos
            # - lineno
            # - type
            # - value
            if tok.value == "{":
                if (prevNWS is not None) and (prevNWS.type == "="):
                    valueCloser = "}"
                    collect("[", path, tok.lineno)
                    # ^ to convert to list
                else:
                    indent += one_tab
                    collect("\n"+indent, path, tok.lineno)
            elif tok.value == "}":
                if valueCloser == "}":
                    collect("]", path, tok.lineno)
                    # ^ to convert to list
                    valueCloser = ""
                else:
                    if len(indent) >= len(one_tab):
                        indent = indent[:len(indent)-len(one_tab)]
                        collect("\n"+indent, path, tok.lineno)
                    else:
                        raise SyntaxError("{}:{}: unexpected '}'"
                                          "".format(p.source,
                                                    tok.lineno))
            elif tok.value == ";":
                # if program.showAll:
                #     sys.stdout.write("<;>")
                collect("\n" + indent, path, tok.lineno)
            elif tok.type == "CPP_WS":
                # if program.showAll:
                #     sys.stdout.write("<CPP_WS>")
                newWS = " "
                if "\n" in tok.value:
                    pass
                    # if program.showAll:
                    #     sys.stdout.write("\\n")
                    # newWS = "\n" + indent
                newWS = " "
                if "\n" in tok.value:
                    if unchanged:
                        collect("\n", path, tok.lineno)
                    else:
                        collect(" ", path, tok.lineno)
                else:
                    if unchanged or (not program.endswithWS()):
                        collect(newWS, path, tok.lineno)
            else:
                if "\n" in tok.value:
                    raise RuntimeError("newline shouldn't be in {}"
                                       "".format(tok.type))
                value = tok.value
                # sys.stdout.write("<{}>{}".format(tok.type, value))
                # ^ example:
                '''
<CPP_ID>while<(>(<CPP_ID>count<<><<CPP_ID>limit<&>&<&>&<!>!<CPP_ID>line<.>.<CPP_ID>empty<(>(<)>)<)>)
    <CPP_ID>std<:>:<:>:<CPP_ID>streamsize<CPP_ID>size<=>=<CPP_ID>std<:>:<:>:<CPP_ID>cin<.>.<CPP_ID>rdbuf<(>(<)>)<->-<>>><CPP_ID>in_avail<(>(<)>)
    <CPP_ID>if<(>(<CPP_ID>size<<><<CPP_INTEGER>1<)>)
        <CPP_ID>break
        <CPP_ID>std<:>:<:>:<CPP_ID>getline<(>(<CPP_ID>std<:>:<:>:<CPP_ID>cin<,>,<CPP_ID>line<)>)
    <CPP_ID>if<(>(<!>!<CPP_ID>std<:>:<:>:<CPP_ID>cin<.>.<CPP_ID>eof<(>(<)>)<)>)
        <CPP_ID>this<->-<>>><CPP_ID>addLine<(>(<CPP_ID>line<,>,<CPP_ID>true<)>)
        <CPP_ID>else
        <CPP_ID>break
        <CPP_ID>count<+>+<+>+
                '''
                collect(tok.value, path, tok.lineno)
            if tok.type != "CPP_WS":
                prevNWS = tok
            prevTok = tok

    def pair_with_prev(self, s):
        if len(self._parts) < 1:
            return False
        for key, signs in self.multis.items():
            if (self._parts[-1] + s) in signs:
                return True
        return False

    def endswithWS(self):
        if len(self._parts) < 1:
            return False
        if len(self._parts[-1].strip()) == 0:
            return True
        return False

    def collect(self, s, path, lineN):
        '''
        Sequential arguments:
        path -- the source code file path for tracing purposes.
        lineN -- the line number (starting with 1) for tracing purposes.
        '''
        # TODO: If int, convert `/` to `//` and import floor division!
        # TODO: deal with types: 'CPP_ID','CPP_INTEGER', 'CPP_FLOAT',
        #                        'CPP_STRING', 'CPP_CHAR', 'CPP_WS',
        #                        'CPP_COMMENT1', 'CPP_COMMENT2',
        #                        'CPP_POUND','CPP_DPOUND'
        #       (listed in cpp-to-py.py or ply/cpp/cpp.py)
        #       and other types such as <

        if s[0] == "\n":
            self.endStatement()
            if s == "\n":
                return
            else:
                s = s[1:]
        if "\n" in s:
            raise ValueError("collect isn't designed"
                             " to accept >1 '\\n'.")
            '''
            parts = s.split("\n")
            lineCount = len(parts)
            if (parts[-1] == '') and (len(parts) > 1):
                # ^ if == 1, may be something like '' (or a string
                #   not containing '\n' which is not this case)
                lineCount -= 1
                # ^ prevent two writes of '' since
                #   " \n".split("\n")
                #   is:
                #   [' ', '']
            for i in range(lineCount):
                self.endStatement(parts[i])
            return
            '''
        # sys.stdout.write(s)
        # self._line += s
        prevPart = ""
        hadIndent = False
        if len(self._parts) > 0:
            prevPart = self._parts[-1]
            if len(prevPart.strip()) == 0:
                hadIndent = True
        if len(s.strip()) == 0:
            if len(self._parts) > 0:
                pass
                '''
                raise ValueError("collect isn't designed to accept"
                                 " spaces other than the opening"
                                 " indent, but the statement already"
                                 " has {}.".format(self._parts))
                '''
            # if (len(prevPart.strip()) != 0) or (len(prevPart) == 0):
            #     self._parts.append(s)

        if self.pair_with_prev(s):
            self._parts[-1] += s
        elif hadIndent and (len(s.strip()) == 0):
            # don't mess up indent
            pass
        else:
            self._parts.append(s)

    def hasStatement(self):
        return len(self._parts) > 0

    def endStatement(self):
        # if "\n" in s:
        #     raise ValueError("endStatement"
        #                      " isn't designed to accept '\\n'.")
        if len(self._parts) < 1:
            sys.stderr.write("[endStatement] INFO:"
                             " there were no more lines\n")
            return False
        # sys.stdout.write(s)
        # self._lines.append(self._line)
        for i in range(len(self._parts)):
            newPart = self.pysigns.get(self._parts[i])
            if newPart is not None:
                self._parts[i] = newPart
            if "\n" in self._parts[i]:
                raise RuntimeError("newline can't be in statement")
        line = None
        if len(self._parts[0].strip()) == 0:
            if len(self._parts) == 1:
                line = self._parts[0] + "pass"
                # If leaving an empty scope, collect "pass".
            else:
                if "\n" in self._parts[0]:
                    raise RuntimeError("newline shouldn't be in tab")
                line = self._parts[0] + " ".join(self._parts[1:])
        else:
            line = " ".join(self._parts)
        self._lines.append(line)
        if self.showAll:
            sys.stderr.write("{}\n".format(self._parts))
        # self._line = ""
        self._parts = []
        return True

    def saveAs(self, path, enable_set_path=True, stream=None):
        '''
        Keyword arguments:
        enable_set_path -- set self.path to path.
        '''
        if self.hasStatement():
            self.endStatement()
            sys.stderr.write("* wrote remaining line\n")
        if enable_set_path:
            self.path = path
        if stream is None:
            with open(path, 'w') as stream:
                for line in self._lines:
                    stream.write(line + "\n")
        else:
            for line in self._lines:
                stream.write(line + "\n")

    def save(self):
        if self.path is None:
            raise RuntimeError("self.path is not set. Try saveAs.")
        self.saveAs(self.path)
