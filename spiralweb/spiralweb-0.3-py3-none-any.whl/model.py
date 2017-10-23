import sys

class SpiralWebChunk():
    lines = []
    options = {}
    name = ''
    type = ''
    parent = None

    def getChunk(self, name):
        for chunk in self.lines:
            if not isinstance(chunk, str):
                if chunk.name == name:
                    return chunk
                elif chunk.getChunk(name) != None:
                    return chunk.getChunk(name)
        return None

    def setParent(self, parent):
        self.parent = parent

        for line in self.lines:
            if not isinstance(line, str):
                line.setParent(parent)

    def dumpLines(self, indentLevel=''):
        output = ''

        for line in self.lines:
            if isinstance(line, str):
                output += line

                if line.find("\n") != -1:
                    output += indentLevel
            else:
                output += line.dumpLines(indentLevel)

        return output

    def hasOutputPath(self):
        return 'out' in self.options.keys()

    def writeOutput(self):
        if self.hasOutputPath():
            content = self.dumpLines()
            path = self.options['out']

            with open(path, 'w') as fileHandle:
                fileHandle.write(content)
        else:
            raise BaseException('No output path specified')

    def __add__(self, exp):
        if isinstance(exp, str):
            for line in self.lines:
                exp += line
            return exp
        else:
            merged = SpiralWebChunk()
            merged.lines = self.lines + exp.lines
            merged.name = self.name
            merged.type = self.type
            merged.parent = self.parent
            merged.options = self.options

            return merged

class SpiralWebRef():
    name = ''
    indentLevel = 0
    parent = None
    type = 'ref'

    def __init__(self, name, indentLevel=''):
        self.name = name
        self.indentLevel = indentLevel

    def __add__(self, exp):
        return exp + self.parent.getChunk(name).dumpLines(indentLevel=self.indentLevel)

    def getChunk(self, name):
        if name == self.name:
            return self
        else:
            return None

    def setParent(self, parent):
        self.parent = parent

    def dumpLines(self, indentLevel=''):
        refChunk = self.parent.getChunk(self.name)

        if refChunk != None:
            return indentLevel + self.indentLevel + refChunk.dumpLines(indentLevel=indentLevel+self.indentLevel)
        else:
            raise BaseException('No chunk named %s found' % self.name)


class SpiralWeb():
    chunks = []
    baseDir = ''

    def __init__(self, chunks=[], baseDir=''):
        self.chunks = chunks
        self.baseDir = baseDir

        for chunk in self.chunks:
            chunk.setParent(self)

    def getChunk(self, name):
        for chunk in self.chunks:
            if chunk.name == name:
                return chunk

        return None

    def tangle(self,chunks=None):
        outputs = {}

        for chunk in self.chunks:
            if chunk.type == 'code':
                if chunk.name in outputs.keys():
                    outputs[chunk.name].lines += chunk.lines
                    outputs[chunk.name].options = dict(list(outputs[chunk.name].options.items()) + list(chunk.options.items()))
                else:
                    outputs[chunk.name] = chunk

        terminalChunks = [x for x in self.chunks if x.hasOutputPath()]

        if chunks != None and len(chunks) > 0:
            for key in chunks:
                if outputs[key].hasOutputPath():
                    outputs[key].writeOutput()
                else:
                    print(outputs[key].dumpLines())
        elif '*' in outputs.keys(): 
            content = outputs['*'].dumpLines()

            if outputs['*'].hasOutputPath():
                outputs['*'].writeOutput()
            else:
                print(content)
        elif len(terminalChunks) > 0:
            for chunk in terminalChunks:
                chunk.writeOutput()
        else:
            raise BaseException('No chunks specified, no chunks with out attributes, and no root chunk defined')
            
        return outputs
    
    def weave(self, chunks=None):
        backend = PandocMarkdownBackend()

        outputs = self.resolveDocumentation()
        backend.output(outputs, chunks)
    def resolveDocumentation(self):
        documentation_chunks = {}
        last_doc = None

        for chunk in self.chunks:
            if (chunk.type == 'doc' and chunk.name != last_doc \
                and chunk.name != ''):
                last_doc = chunk.name
            elif last_doc == None:
                if chunk.type == 'doc':
                    last_doc = chunk.name
                else:
                    doc = SpiralWebChunk()
                    doc.type = 'doc'
                    doc.name = '*'
                    last_doc = '*'

                    documentation_chunks[doc.name] = doc
            
            if last_doc in documentation_chunks:
                documentation_chunks[last_doc].lines.append(chunk)
            else:
                documentation_chunks[last_doc] = chunk

        return documentation_chunks
    
class SpiralWebBackend():
    def dispatchChunk(self, chunk):
        if isinstance(chunk, str):
            return chunk
        elif chunk.type == 'doc':
            return self.formatDoc(chunk)
        elif chunk.type == 'code':
            return self.formatCode(chunk)
        elif chunk.type == 'ref':
            return self.formatRef(chunk)
        else:
                raise BaseException('Unrecognized chunk type (something must have gone pretty badly wrong).')

    def formatDoc(self, chunk):
        return chunk.dumpLines()

    def formatCode(self, chunk):
        return chunk.dumpLines()

    def formatRef(self, chunk):
        return chunk.dumpLines()

    def output(self, topLevelDocs, chunksToOutput):
        terminalChunks = [x for w, x in topLevelDocs.items() \
                          if x.type == 'doc' and x.hasOutputPath()]

        if chunksToOutput != None and len(chunksToOutput) > 0:
            for key in topLevelDocs:
                if topLevelDocs[key].type == 'doc':
                    if topLevelDocs[key].hasOutputPath():
                        self.writeOutChunk(topLevelDocs[key])
                    else:
                        print(self.dispatchChunk(topLevelDocs[key]))
        elif len(terminalChunks) > 0:
            for chunk in terminalChunks:
                self.writeOutChunk(chunk)
        else:
            for name, chunk in topLevelDocs.items():
                print(self.dispatchChunk(chunk))

    def writeOutChunk(self, chunk):
        if not 'out' in chunk.options:
            raise BaseException('When writing out a chunk with writeOutChunk an output parameter is expected')
        else:
            with open(chunk.options['out'], 'w') as outFile:
                outFile.write(self.dispatchChunk(chunk))
    
class PandocMarkdownBackend(SpiralWebBackend):
    def formatDoc(self, chunk):
        lines = [self.dispatchChunk(x) for x in chunk.lines] 
        return ''.join(lines)

    def formatCode(self, chunk):
        leader = "~~~~~~~~~~~~~~~~~"
        options = ''

        if chunk.options.get('lang') != None:
            options = '{.%(language)s .numberLines}' % \
                {'language': chunk.options.get('lang')}

        lines = [self.dispatchChunk(x) for x in chunk.lines]

        return "%(leader)s%(options)s\n%(code)s%(trailer)s\n" % \
            {"leader": leader, "code": ''.join(lines),
             "trailer": leader, "options": options}

    def formatRef(self, chunk):
        return "<%(name)s>" % {"name": chunk.name}

