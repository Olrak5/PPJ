import enum
import sys
import traceback
import os

inputLines = []

for line in sys.stdin:
    inputLines.append(line.rstrip())

globalScope = []
globalCode = ''
globalLoopNum = 0

class Node:
    class decodeType(enum.Enum):
        VAR = 1
        NUM = 2
        CHAR = 3
        STR = 4
        FUNC = 5

    def __init__(self, depth : int, content : str):
        self.depth = depth
        self.content = content
        self.parent = None
        self.children = []
        self.characterTable = None
        self.scopeNode = None
        self.type = None
        self.lExpression = None
        self.names = None
        self.ntype = None
        self.elemNum = None
        self.code = None
        self.data = {}
        self.scope = None
        self.scopeLayerNum = 0
        self.decode = None
        self.value = None
        self.size = None
        self.lStart = None
        self.lEnd = None
        self.inc = False


    def addChild(self, node):
        self.children += [node]


rootNode = Node(0, inputLines[0])
rootNode.characterTable = {}
prevNode = rootNode


def scopeDiscplacement(varName, scope):
    found = False
    size = 0
    isPointer = False
    inFirst = False
    for i in reversed(range(len(scope))):
        subScope = scope[i]
        for j in reversed(range(len(subScope))):
            item = subScope[j]
            if not found:
                if item[0] == varName:
                    if i != 0:
                        size += 1
                    else:
                        inFirst = True
                    found = True
                    if len(item) == 3:
                        isPointer = True
            else:
                size += item[1]
    return found, size, isPointer, inFirst

def scopeDiscplacementextra(varName, scope):
    found = False
    size = 0
    isPointer = False
    inFirst = False
    for i in reversed(range(len(scope))):
        subScope = scope[i]
        for j in reversed(range(len(subScope))):
            item = subScope[j]
            if not found:
                if item[0] == varName:
                    if item[1] != 1:
                        isPointer = True
                    if i != 0:
                        size += 1
                    else:
                        inFirst = True
                    found = True
                    if len(item) == 3:
                        isPointer = True
            else:
                size += item[1]
    return found, size, isPointer, inFirst

def isInGlobal(varName):
    global globalScope
    found = False
    for item in globalScope:
        if item[0] == varName:
            found = True
            break
    return found

def loadVarCode(varName : str, scope : list, regName : str):
    if scope != None:
        found, size, isPointer, inFirst = scopeDiscplacement(varName, scope)
    if scope != None and found:
        if isPointer:
            return \
                ' POP ' + regName + '\n' +\
                ' PUSH R5\n' +\
                ' MOVE ' + regName + ', R5\n' +\
                ' MOVE R6, ' + regName + '\n' +\
                ' LOAD ' + regName + ', (' + regName + ') \n' +\
                ' ADD R5, %D ' + str(size) + ', R5\n' + \
                ' SHL R5, %D 2, R5\n' + \
                ' SUB ' + regName + ', R5, ' + regName + '\n' + \
                ' POP R5\n' +\
                ' STORE R0, (' + regName + ')\n'
        else:
            return \
                ' POP ' + regName + '\n' + \
                ' PUSH R5\n' + \
                ' MOVE ' + regName + ', R5\n' + \
                ' MOVE R6, ' + regName + '\n' + \
                ' ADD R5, %D ' + str(size + 1 - (int)(inFirst)) + ', R5\n' + \
                ' SHL R5, %D 2, R5\n' + \
                ' SUB ' + regName + ', R5, ' + regName + '\n' + \
                ' POP R5\n' + \
                ' LOAD ' + regName + ', (' + regName + ')\n'
        #' LOAD ' + regName + ', (R6 - ' + str((size+varPos+1)*4) + ')\n'
    else:
        found = isInGlobal(varName)
        if found:
            return \
                ' POP ' + regName + '\n' + \
                ' PUSH R5\n' + \
                ' MOVE ' + regName + ', R5\n' + \
                ' MOVE g_' + str(varName) + ', ' + regName + '\n' + \
                ' SHL R5, %D 2, R5\n' + \
                ' ADD ' + regName + ', R5, ' + regName + '\n' + \
                ' POP R5\n' + \
                ' LOAD ' + regName + ', (' + regName + ')\n'
                # ' LOAD ' + regName + ', (g_' + str(varPos) + '_' + varName + ')\n'
        else:
            raise Exception('Variable not found: ' + varName)

def loadVarLocation(varName : str, scope : list):
    if scope != None:
        found, size, isPointer, inFirst = scopeDiscplacement(varName, scope)
    if scope != None and found:
        return \
            ' MOVE 0, R0\n' + \
            ' PUSH R5\n' + \
            ' MOVE R0, R5\n' + \
            ' MOVE R6, R0\n' + \
            ' ADD R5, %D ' + str(size + 1 - (int)(inFirst)) + ', R5\n' + \
            ' SHL R5, %D 2, R5\n' + \
            ' SUB R0, R5, R0\n' + \
            ' POP R5\n'
    else:
        found = isInGlobal(varName)
        if found:
            return \
                ' MOVE g_' + str(varName) + ', R0\n'
                # ' LOAD ' + regName + ', (g_' + str(varPos) + '_' + varName + ')\n'
        else:
            raise Exception('Variable not found: ' + varName)

def saveVarCode(varName : str, scope : list, regName : str, freeReg : str):
    if scope != None:
        found, size, isPointer, inFirst = scopeDiscplacement(varName, scope)
    if scope != None and found:
        if isPointer:
            return \
                ' POP ' + freeReg + '\n' +\
                ' PUSH R5\n' +\
                ' MOVE ' + freeReg + ', R5\n' +\
                ' MOVE R6, ' + freeReg + '\n' +\
                ' LOAD ' + freeReg + ', (' + freeReg + ') \n' +\
                ' ADD R5, %D ' + str(size) + ', R5\n' + \
                ' SHL R5, %D 2, R5\n' + \
                ' SUB ' + freeReg + ', R5, ' + freeReg + '\n' + \
                ' POP R5\n' +\
                ' STORE ' + regName + ', (' + freeReg + ')\n'
        else:
            return \
                ' POP ' + freeReg + '\n' +\
                ' PUSH R5\n' +\
                ' MOVE ' + freeReg + ', R5\n' +\
                ' MOVE R6, ' + freeReg + '\n' +\
                ' ADD R5, %D ' + str(size + 1 - (int)(inFirst)) + ', R5\n' +\
                ' SHL R5, %D 2, R5\n' +\
                ' SUB ' + freeReg + ', R5, ' + freeReg + '\n' +\
                ' POP R5\n' +\
                ' STORE ' + regName + ', (' + freeReg + ')\n'
        # return ' SAVE ' + regName + ', (R6 - ' + str((size + varPos + 1) * 4) + ')\n'
    else:
        found = isInGlobal(varName)
        if found:
            return \
                ' POP ' + freeReg + '\n' + \
                ' PUSH R5\n' + \
                ' MOVE ' + freeReg + ', R5\n' + \
                ' MOVE g_' + str(varName) + ', ' + freeReg + '\n' + \
                ' SHL R5, %D 2, R5\n' + \
                ' ADD ' + freeReg + ', R5, ' + freeReg + '\n' + \
                ' POP R5\n' + \
                ' STORE ' + regName + ', (' + freeReg + ')\n'
            # ' SAVE ' + regName + ', (g_' + str(varPos) + '_' + varName + ')\n'
        else:
            raise Exception('Variable not found: ' + varName)

def findScopeNode(node):
    if node.parent.characterTable != None:
        return node.parent
    elif node.parent.scopeNode != None:
        return node.parent.scopeNode

def createScope(curNode, prevNode):
    curNode.scopeNode = findScopeNode(curNode)
    if curNode.content == '<slozena_naredba>':
        curNode.characterTable = {}

for line in inputLines[1:]:
    curDepth = len(line) - len(line.lstrip())
    if curDepth <= prevNode.depth:
        while prevNode.depth != curDepth-1:
            prevNode = prevNode.parent
    curNode = Node(curDepth, line.lstrip())
    curNode.parent = prevNode
    prevNode.addChild(curNode)
    createScope(curNode, prevNode)
    prevNode = curNode

def printCurTree(node):
    print(' '*node.depth + node.content)
    for child in node.children:
        printCurTree(child)

# printCurTree(rootNode)

def formatNodeException(node):
    text = ''
    text += node.content
    text += ' ::='
    for child in node.children:
        if child.content[0] != '<':
            name, lineNum, content = child.content.split()
            text += ' ' + name + '(' + lineNum + ',' + content + ')'
        else:
            text += ' ' + child.content
    return text

def getCharacterUniformName(character : str):
    return character.split()[0]

def getCharacterName(character):
    return character.split()[2]

def getProductionText(node):
    # print(node.children)
    return ' '.join([getCharacterUniformName(child.content) for child in node.children])

def declaredInNode(node, name):
    table = node.characterTable
    checkNode = node

    if node.characterTable == None:
        if node.scopeNode == None:
            return None
        table = node.scopeNode.characterTable
        checkNode = node.scopeNode

    if name in table.keys():
        return node
    else:
        return declaredInNode(node.scopeNode, name)

def isInt(character):
    try:
        value = int(character)
    except ValueError:
        return False
    return value >= -2**31 and value <= 2**32

def isChar(character):
    if character[0] != '\'' and character[-1] != '\'':
        return False
    if (len(character[1:-1]) == 1 and ord(character[1]) < 256) or character[1:-1] == "'\\t'" \
        or character[1:-1] == "'\\n'" or character[1:-1] == "'\\0'" \
        or character[1:-1] == "'\\''" or character[1:-1] == "'\\\""\
        or character[1:-1] == "'\\\\'":
        return True
    return False

def isString(character):
    if character[0] != '\"' and character[-1] != '\"':
        return False
    strLen = len(character) - 2
    i = 0
    while i < strLen:
        if character[i+1] == '\\' and i < strLen-1:
            if not isChar('\'' + character[i+1:i+3] + '\''):
                return False
        if not isChar('\'' + character[i+1] + '\''):
            return False
        i+=1
    return True

def isConst(character):
    if character == 'const(int)' or character == 'const(char)':
        return character[6:-1]
    return False

def isArray(character):
    if len(character) < 5:
        return False
    else:
        if character[0:4] == 'niz(' and character[-1] == ')':
            return character[4:-1]
        else:
            return False

def isVoid(character):
    return character == 'void'

def isArguemntType(character):
    return character == 'int' or character == 'char'

def isFunction(character):
    if len(character) < 11:
        return False
    if character[0:9] == 'funkcija(' and character[-1] == ')':
        if len(character[9:-1].split('->')) != 2:
            return False
        if isArguemntType(character[9:-1].split('->')[1]) or \
            isVoid(character[9:-1].split('->')[1]):
            return False
        if character[9:-1].split('->')[0][0] != '[' and \
            character[9:-1].split('->')[0][-1] != ']':
            if not isVoid(character[9:-1].split('->')[0]):
                return False
        if character[9:-1].split('->')[0][0] != '[' or \
            character[9:-1].split('->')[0][-1] != ']':
            return False
        for c in character[9:-1].split('->')[0].split(','):
            if not isArguemntType(c):
                return False
        return True
        
    else:
        return False

def canImplicitlyChange(type1, type2):
    if type1 == type2:
        return True
    if isConst(type1) != False and not isConst(type2):
        if isConst(type1) == type2:
            return True
        return canImplicitlyChange(isConst(type1), type2)
    elif not isConst(type1) and isConst(type2):
        if type1 == isConst(type2):
            return True
        return canImplicitlyChange(type1, isConst(type2))
    elif type1 == 'char' and type2 == 'int':
        return True
    elif isArray(type1) != False and isArray(type2) != False:
        if isConst(isArray(type1)) == False and isConst(isArray(type2)) != False:
            if isArray(type1) == isConst(isArray(type2)):
                return True
            else:
                return False
        else:
            return False
    else:
        return False

def canBeCastTo(type1, type2):
    if canImplicitlyChange(type1, type2):
        return True
    else:
        if type1 == 'int' and type2 == 'char':
            return True
        else:
            return False

def getChildrenCode(node):
    code = ''
    for child in node.children:
        code += child.code
    return code

# EXPRESSIONS

def calculate_primarni_izraz(node):
    productionText = getProductionText(node)
    if productionText == 'BROJ':
        node.value = int(getCharacterName(node.children[0].content))
    elif productionText == 'ZNAK':
        node.value = ord(getCharacterName(node.children[0].content)[1])
    elif productionText == 'NIZ_ZNAKOVA':
        node.value = [ord(c) for c in getCharacterName(node.children[0].content)]
    else:
        raise Exception('calculate primary:' + productionText)

def primarni_izraz(node):
    productionText = getProductionText(node)
    if productionText == 'IDN':
        node.parent.decode = Node.decodeType.VAR
        node.code = getCharacterName(node.children[0].content)
        # name = getCharacterName(node.children[0].content)
        # declaredNode = declaredInNode(node, name)
        # if declaredNode == None:
        #     raise Exception(formatNodeException(node))
        # else:
        #     node.type = declaredNode.characterTable[name].type
        #     node.lExpression = declaredNode.characterTable[name].lExpression
    elif productionText == 'BROJ':
        node.parent.decode = Node.decodeType.NUM
        node.code = getCharacterName(node.children[0].content)
        # print((int(getCharacterName(node.children[0].content)) & 0xffff0000) >> 6 <<4)
        # MOVE 1234, R3
        # ROTL R3, %D 16, R3
        # ADD R3, 5678, R3

        # name = getCharacterName(node.children[0].content)
        # if not isInt(name):
        #     raise Exception(formatNodeException(node))
        # else:
        #     node.type = 'int'
        #     node.lExpression = 0
    elif productionText == 'ZNAK':
        node.parent.decode = Node.decodeType.CHAR
        node.code = getCharacterName(node.children[0].content)[1]
        # name = getCharacterName(node.children[0].content)
        # if not isChar(name):
        #     raise Exception(formatNodeException(node))
        # else:
        #     node.type = 'char'
        #     node.lExpression = 0
    elif productionText == 'NIZ_ZNAKOVA':
        node.parent.decode = Node.decodeType.STR
        node.code = getCharacterName(node.children[0].content)
        # name = getCharacterName(node.children[0].content)
        # if not isString(name):
        #     raise Exception(formatNodeException(node))
        # else:
        #     node.type = 'niz(const(char))'
        #     node.lExpression = 0
    elif productionText == 'L_ZAGRADA <izraz> D_ZAGRADA':
        node.children[1].scope = node.scope
        check(node.children[1])
        node.code = node.children[1].code
        #
        # node.type = node.children[1].type
        # node.lExpression = node.children[1].lExpression

def calculate_postfiks_izraz(node):
    productionText = getProductionText(node)
    if productionText == '<primarni_izraz>':
        calculate_primarni_izraz(node.children[0])

        node.value = node.children[0].value

    elif productionText == '<postfiks_izraz> OP_INC' or \
            productionText == '<postfiks_izraz> OP_DEC':
        calculate_postfiks_izraz(node.children[0])
        temp = productionText.split()[1]
        if temp == 'OP_INC':
            node.value = node.children[1].value + 1
        elif temp == 'OP_DEC':
            node.value = node.children[1].value - 1
    else:
        raise Exception('calculate postfix error:' + productionText)

def postfiks_izraz(node):
    productionText = getProductionText(node)
    if productionText == '<primarni_izraz>':
        node.children[0].scope = node.scope
        check(node.children[0])

        node.code = node.children[0].code
        node.parent.decode = node.decode
        node.inc = node.children[0].inc

        # node.type = node.children[0].type
        # node.lExpression = node.children[0].lExpression
    elif productionText == '<postfiks_izraz> L_UGL_ZAGRADA <izraz> D_UGL_ZAGRADA':
        node.decode = None
        node.children[0].scope = node.scope
        check(node.children[0])
        node.children[2].scope = node.scope
        check(node.children[2])
        if node.parent.content != '<izraz_pridruzivanja>':
            node.code =\
                node.children[2].code + '\n' +\
                loadVarCode(node.children[0].code, node.scope, 'R0') + '\n' +\
                ' PUSH R0\n'
        else:
            node.code = node.children[0].code
            node.elemNum = node.children[2].code


        # if isArray(node.children[0].type) != False:
        #     if not( isConst(node.children[0].type) or\
        #          isArguemntType(node.children[0].type) ):
        #         raise Exception(formatNodeException(node))
        # else:
        #     raise Exception(formatNodeException(node))
        # if not canImplicitlyChange(node.children[2].type, 'int'):
        #     raise Exception(formatNodeException(node))
        # node.type = node.children[0].type
        # node.lExpression = (not isConst(node.children[0].type))
    elif productionText == '<postfiks_izraz> L_ZAGRADA D_ZAGRADA':
        node.decode = None
        node.children[0].scope = node.scope
        check(node.children[0])
        node.code =\
            ' PUSH R6\n' +\
            ' MOVE R7, R6\n' +\
            ' CALL f_' + node.children[0].code + '\n' +\
            ' MOVE R6, R0\n' +\
            ' POP R6\n' +\
            ' PUSH R0\n'
        # check(node.children[0])
        # if not node.children[0].type[:17] == 'funkcija(void ->':
        #     raise Exception(formatNodeException(node))
        # node.type = node.children[0].type.split('->')[1].split(')')[0].strip()
        # node.lExpression = 0
    elif productionText == '<postfiks_izraz> L_ZAGRADA <lista_argumenata> D_ZAGRADA':
        node.decode = None
        node.children[0].scope = node.scope
        check(node.children[0])
        node.children[2].scope = node.scope
        check(node.children[2])
        node.code = \
            ' PUSH R6\n' + \
            node.children[2].code + '\n' +\
            ' MOVE R7, R6\n' +\
            ' ADD R6, %D ' + str((node.children[2].elemNum - 1)*4) + ', R6\n' +\
            ' CALL f_' + node.children[0].code + '\n' + \
            ' MOVE R6, R0\n' + \
            ' POP R6\n' * node.children[2].elemNum +\
            ' POP R6\n' + \
            ' PUSH R0\n'

        # ' SUB R6, 4, R6\n\n' + \
        # if not isFunction(node.children[0].type):
        #     raise Exception(formatNodeException(node))
        # params = node.children[0].type.split('->')[0].split('(').split()
        # if len(params) != len(node.children[2].type):
        #     raise Exception(formatNodeException(node))
        # for i in range(len(params)):
        #     if not canImplicitlyChange(node.children[2].type[i], params[i]):
        #         raise Exception(formatNodeException(node))
        # node.type = node.children[0].type.split('->')[1].split(')')[0].strip()
        # node.lExpression = 0
    elif productionText == '<postfiks_izraz> OP_INC' or \
            productionText == '<postfiks_izraz> OP_DEC':
        node.children[0].scope = node.scope
        check(node.children[0])
        temp = productionText.split()[1]
        if temp == 'OP_INC':
            node.code = \
                ' XOR R0, R0, R0\n' + \
                ' PUSH R0\n' +\
                loadVarCode(node.children[0].code, node.scope, 'R0') + '\n' + \
                ' ADD R0, 1, R0\n' + \
                ' XOR R1, R1, R1\n' + \
                ' PUSH R1\n' + \
                saveVarCode(node.children[0].code, node.scope, 'R0', 'R3') + '\n'
        elif temp == 'OP_DEC':
            node.code = \
                ' XOR R1, R1, R1\n' + \
                ' PUSH R1\n' + \
                loadVarCode(node.children[0].code, node.scope, 'R0') + '\n' + \
                ' SUB R0, 1, R0\n' + \
                ' XOR R1, R1, R1\n' + \
                ' PUSH R1\n' + \
                saveVarCode(node.children[0].code, node.scope, 'R0', 'R3') + '\n'
        node.code += ' SUB R0, 1, R0\n PUSH R0\n'
        node.inc = False
        # if node.children[0].lExpression != 1 or \
        #     canImplicitlyChange(node.children[0].type, 'int'):
        #     raise Exception(formatNodeException(node))
        # node.type = 'int'
        # node.lExpression = 0

def lista_argumenata(node):
    productionText = getProductionText(node)
    if productionText == '<izraz_pridruzivanja>':
        node.children[0].scope = node.scope
        check(node.children[0])
        node.code = node.children[0].code
        node.elemNum = 1
        # node.type = [node.children[0].type]
    elif productionText == '<lista_argumenata> ZAREZ <izraz_pridruzivanja>':
        node.children[0].scope = node.scope
        check(node.children[0])
        node.children[2].scope = node.scope
        check(node.children[2])
        node.code = node.children[0].code + '\n' + node.children[2].code
        node.elemNum = node.children[0].elemNum + 1
        # node.type = node.children[0].type + [node.children[2].type]

def calculate_unarni_izraz(node):
    productionText = getProductionText(node)
    if productionText == '<postfiks_izraz>':
        calculate_postfiks_izraz(node.children[0])

        node.value = node.children[0].value
    elif productionText == 'OP_INC <unarni_izraz>' or \
            productionText == 'OP_DEC <unarni_izraz>':
        calculate_unarni_izraz(node.children[1])
        temp = productionText.split()[0]
        if temp == 'OP_INC':
            node.value = node.children[1].value + 1
        elif temp == 'OP_DEC':
            node.value = node.children[1].value - 1
    elif productionText == '<unarni_operator> <cast_izraz>':
        calculate_cast_izraz(node.children[1])
        temp = getCharacterUniformName(node.children[0].children[0].content)
        if temp == 'PLUS':
            node.value = node.children[1].value
        elif temp == 'MINUS':
            node.value = -node.children[1].value
        elif temp == 'OP_TILDA':
            node.value = ~ node.children[1].value
        elif temp == 'OP_NEG':
            node.value = not node.children[1].value
        
def unarni_izraz(node):
    productionText = getProductionText(node)
    if productionText == '<postfiks_izraz>':
        node.children[0].scope = node.scope
        check(node.children[0])
        node.inc = node.children[0].inc

        if node.decode == Node.decodeType.NUM:
            node.code = \
                ' MOVE %D ' + str((int(node.children[0].code) & 0xffff0000) >> 16) + ', R0\n' + \
                ' ROTL R0, %D 16, R0\n' + \
                ' ADD R0, %D ' + str((int(node.children[0].code) & 0x0000ffff)) + ', R0\n' + \
                ' PUSH R0\n'
        elif node.decode == Node.decodeType.VAR:
            found, size, isPointer, inFirst = scopeDiscplacementextra(node.children[0].code, node.scope)
            if node.parent.content == '<unarni_izraz>':
                node.code = node.children[0].code
            elif isPointer:
                node.code = \
                    loadVarLocation(node.children[0].code, node.scope) + '\n' + \
                    ' PUSH R0\n'
            else:
                node.code = \
                    ' XOR R1, R1, R1\n' + \
                    ' PUSH R1\n' + \
                    loadVarCode(node.children[0].code, node.scope, 'R0') + '\n' +\
                    ' PUSH R0\n'
        elif node.decode == Node.decodeType.CHAR:
            node.code = \
                ' MOVE %D ' + str(ord(node.children[0].code)) + ', R0\n' + \
                ' PUSH R0\n'
        elif node.decode == Node.decodeType.STR:
            raise Exception('String association: ' + productionText)
        else:
            node.code = node.children[0].code
    elif productionText == 'OP_INC <unarni_izraz>' or\
            productionText == 'OP_DEC <unarni_izraz>':
        node.children[1].scope = node.scope
        check(node.children[1])
        temp = productionText.split()[0]
        if temp == 'OP_INC':
            node.code = \
                ' XOR R0, R0, R0\n' +\
                ' PUSH R0\n' +\
                loadVarCode(node.children[1].code, node.scope, 'R0') + '\n' +\
                ' ADD R0, 1, R0 ;OP_INC\n' + \
                ' MOVE 0, R4\n' +\
                ' PUSH R4\n' +\
                saveVarCode(node.children[1].code, node.scope, 'R0', 'R4') + '\n' +\
                ' PUSH R0\n'
        elif temp == 'OP_DEC':
            node.code = \
                ' XOR R0, R0, R0\n' + \
                ' PUSH R0\n' +\
                loadVarCode(node.children[1].code, node.scope, 'R0') + '\n' + \
                ' SUB R0, 1, R0 ;OP_DEC\n' + \
                ' MOVE 0, R4\n' +\
                ' PUSH R4\n' +\
                saveVarCode(node.children[1].code, node.scope, 'R0', 'R4') + '\n' +\
                ' PUSH R0\n'
        node.inc = False
        # if node.children[1].lExpression != 1:
        #     raise Exception(formatNodeException(node))
        # if not canImplicitlyChange(node.children[1].type, 'int'):
        #     raise Exception(formatNodeException(node))
        # node.type = 'int'
        # node.lExpression = 0
    elif productionText == '<unarni_operator> <cast_izraz>':
        node.children[1].scope = node.scope
        check(node.children[1])
        # if not canImplicitlyChange(node.children[1].type, 'int'):
        #     raise Exception(formatNodeException(node))
        # node.type = 'int'
        # node.lExpression = 0
        temp = getCharacterUniformName(node.children[0].children[0].content)
        if temp == 'PLUS':
            node.code = node.children[1].code
        elif temp == 'MINUS':
            node.code = node.children[1].code + '\n' +\
                ' POP R0\n' +\
                ' XOR R0, -1, R0\n' +\
                ' ADD R0, 1, R0\n' +\
                ' PUSH R0\n'
        elif temp == 'OP_TILDA':
            node.code = node.children[1].code + '\n' + \
                ' POP R0\n' + \
                ' XOR R0, -1, R0\n' + \
                ' PUSH R0\n'
        elif temp == 'OP_NEG':
            node.code = node.children[1].code + '\n' + \
                ' POP R0\n' + \
                ' XOR R1, R1, R1\n' +\
                ' CMP R0, R1\n' +\
                ' ADD_NE R1, 1, R1\n' + \
                ' PUSH R1\n'
        if node.children[1].inc:
            node.code = ' PUSH R0\n' + node.code

def calculate_cast_izraz(node):
    productionText = getProductionText(node)
    if productionText == '<unarni_izraz>':
        calculate_unarni_izraz(node.children[0])

        node.value = node.children[0].value
    elif productionText == 'L_ZAGRADA <ime_tipa> D_ZAGRADA <cast_izraz>':
        calculate_unarni_izraz(node.children[3])
        node.value = node.children[3].value

def cast_izraz(node):
    productionText = getProductionText(node)
    if productionText == '<unarni_izraz>':
        node.children[0].scope = node.scope
        check(node.children[0])
        node.code = node.children[0].code
        node.inc = node.children[0].inc
    elif productionText == 'L_ZAGRADA <ime_tipa> D_ZAGRADA <cast_izraz>':
        node.children[1].scope = node.scope
        check(node.children[1])
        node.children[3].scope = node.scope
        check(node.children[3])
        node.code = node.children[3].code
        if node.children[3].inc:
            node.code = ' PUSH R0\n' + node.code
        # if not canBeCastTo(node.children[3].type, node.children[1].type):
        #     raise Exception(formatNodeException(node))
        # node.type = node.children[1].type
        # node.lExpression = 0

def ime_tipa(node):
    productionText = getProductionText(node)
    if productionText == '<specifikator_tipa>':
        check(node.children[0])
        node.type = node.children[0].type
        node.code = node.children[0].code
    elif productionText == 'KR_CONST <specifikator_tipa>':
        check(node.children[1])
        node.type = node.children[1].type
        node.code = node.children[1].code
        # if node.children[1].type == 'void':
        #     raise Exception(formatNodeException(node))
        # node.type = 'const(' + node.children[1].type + ')'

def specifikator_tipa(node):
    productionText = getProductionText(node)
    if productionText == 'KR_VOID':
        node.code = getCharacterName(node.children[0].content)
        node.type = 'void'
    elif productionText == 'KR_CHAR':
        node.code = getCharacterName(node.children[0].content)
        node.type = 'char'
    elif productionText == 'KR_INT':
        node.code = getCharacterName(node.children[0].content)
        node.type = 'int'

def calculate_multiplikativni_izraz(node):
    productionText = getProductionText(node)
    if productionText == '<cast_izraz>':
        calculate_cast_izraz(node.children[0])
        node.value = node.children[0].value
    elif productionText == '<multiplikativni_izraz> OP_PUTA <cast_izraz>' or \
            '<multiplikativni_izraz> OP_DIJELI <cast_izraz>' or \
            '<multiplikativni_izraz> OP_MOD <cast_izraz>':
        calculate_multiplikativni_izraz(node.children[0])
        calculate_cast_izraz(node.children[2])
        temp = productionText.split()[1]
        if temp == 'OP_PUTA':
            node.value = node.children[0].value * node.children[2].value
        elif temp == 'OP_DIJELI':
            node.value = node.children[0].value / node.children[2].value
        elif temp == 'OP_MOD':
            node.value = node.children[0].value % node.children[2].value

def multiplikativni_izraz(node):
    global globalLoopNum
    productionText = getProductionText(node)
    if productionText == '<cast_izraz>':
        node.children[0].scope = node.scope
        check(node.children[0])
        node.code = node.children[0].code
        node.inc = node.children[0].inc
    elif productionText == '<multiplikativni_izraz> OP_PUTA <cast_izraz>' or \
            '<multiplikativni_izraz> OP_DIJELI <cast_izraz>' or \
            '<multiplikativni_izraz> OP_MOD <cast_izraz>':
        node.children[0].scope = node.scope
        check(node.children[0])
        # if not canImplicitlyChange(node.children[0], 'int'):
        #     raise Exception(formatNodeException(node))
        node.children[2].scope = node.scope
        check(node.children[2])
        # if not canImplicitlyChange(node.children[2], 'int'):
        #     raise Exception(formatNodeException(node))
        # node.type = 'int'
        # node.lExpression = 0
        node.code = ''
        if node.children[0].inc:
            node.code = ' PUSH R0\n'
        node.code += node.children[0].code + '\n'
        if node.children[1].inc:
            node.code = ' PUSH R0\n' + node.code
        node.code += node.children[2].code + '\n'
        temp = productionText.split()[1]
        if temp == 'OP_PUTA':
            node.code +=\
            ' POP R0\n' +\
            ' POP R1\n' +\
            ' MOVE 0, R2\n' +\
            ' XOR R0, R1, R3 \n' +\
            'l_' + str(globalLoopNum) + \
            ' OR R0, R0, R0 \n' +\
            ' JR_P l_' + str(globalLoopNum+2) + ' \n' +\
            'l_' + str(globalLoopNum+1) + \
            ' XOR R0, -1, R0 \n' +\
            ' ADD R0, 1, R0 \n' +\
            'l_' + str(globalLoopNum+2) + \
            ' OR R1, R1, R1 \n' +\
            ' JR_P l_' + str(globalLoopNum+4) + ' \n' +\
            'l_' + str(globalLoopNum+3) + \
            ' XOR R1, -1, R1 \n' +\
            ' ADD R1, 1, R1 \n' +\
            'l_' + str(globalLoopNum+4) + \
            ' ADD R0, R2, R2 \n' +\
            ' SUB R1, 1, R1 \n' +\
            ' JR_NZ l_' + str(globalLoopNum+4) + '\n' +\
            'l_' + str(globalLoopNum+5) + \
            ' ROTL R3, 1, R3 \n' +\
            ' JR_NC l_' + str(globalLoopNum+7) + '\n' +\
            'l_' + str(globalLoopNum+6) + \
            ' XOR R2, -1, R2 \n' +\
            ' ADD R2, 1, R2 \n' +\
            'l_' + str(globalLoopNum+7) + \
            ' PUSH R2\n' + '\n'
            globalLoopNum += 8
        elif temp == 'OP_DIJELI':
            node.code += \
            ' POP R0\n' + \
            ' POP R1\n' + \
            ' MOVE 0, R2\n' +\
            'l_' + str(globalLoopNum) + \
            ' OR R0, R0, R0 \n' + \
            ' JR_P l_' + str(globalLoopNum + 2) + ' \n' + \
            'l_' + str(globalLoopNum + 1) + \
            ' XOR R0, -1, R0 \n' + \
            ' ADD R0, 1, R0 \n' + \
            'l_' + str(globalLoopNum + 2) + \
            ' OR R1, R1, R1 \n' + \
            ' JR_P l_' + str(globalLoopNum + 4) + ' \n' + \
            'l_' + str(globalLoopNum + 3) + \
            ' XOR R1, -1, R1 \n' + \
            ' ADD R1, 1, R1 \n' + \
            'l_' + str(globalLoopNum + 4) + \
            ' CMP R1, R0 \n' + \
            ' JR_N ' + 'l_' + str(globalLoopNum + 5) + '\n' +\
            ' SUB R1, R0, R1\n' + \
            ' ADD R2, 1, R2\n' +\
            ' JR l_' + str(globalLoopNum + 4) + '\n' + \
            'l_' + str(globalLoopNum + 5) + \
            ' ROTL R3, 1, R3 \n' + \
            ' JR_NC l_' + str(globalLoopNum + 7)+ '\n' \
            'l_' + str(globalLoopNum + 6) + \
            ' XOR R2, -1, R2 \n' + \
            ' ADD R2, 1, R2 \n' + \
            'l_' + str(globalLoopNum + 7) + \
            ' PUSH R2\n' + '\n'
            globalLoopNum += 8
        elif temp == 'OP_MOD':
            node.code += \
            ' POP R0\n' + \
            ' POP R1\n' + \
            'l_' + str(globalLoopNum) + \
            ' OR R0, R0, R0 \n' + \
            ' JR_P l_' + str(globalLoopNum + 2) + ' \n' + \
            'l_' + str(globalLoopNum + 1) + \
            ' XOR R0, -1, R0 \n' + \
            ' ADD R0, 1, R0 \n' + \
            'l_' + str(globalLoopNum + 2) + \
            ' OR R1, R1, R1 \n' + \
            ' JR_P l_' + str(globalLoopNum + 4) + ' \n' + \
            'l_' + str(globalLoopNum + 3) + \
            ' XOR R1, -1, R1 \n' + \
            ' ADD R1, 1, R1 \n' + \
            'l_' + str(globalLoopNum + 4) + \
            ' CMP R1, R0 \n' + \
            ' JR_N ' + 'l_' + str(globalLoopNum + 5) + '\n' + \
            ' SUB R1, R0, R1\n' + \
            ' JR l_' + str(globalLoopNum + 4) + '\n' + \
            'l_' + str(globalLoopNum + 5) + \
            ' ROTL R3, 1, R3 \n' + \
            ' JR_NC l_' + str(globalLoopNum + 7) + '\n' \
            'l_' + str(globalLoopNum + 6) + \
            ' XOR R1, -1, R1 \n' + \
            ' ADD R1, 1, R1 \n' + \
            'l_' + str(globalLoopNum + 7) + \
            ' PUSH R1\n' + '\n'
            globalLoopNum += 8

def calculate_aditivni_izraz(node):
    productionText = getProductionText(node)
    if productionText == '<multiplikativni_izraz>':
        calculate_multiplikativni_izraz(node.children[0])

        node.value = node.children[0].value
    elif productionText == '<aditivni_izraz> PLUS <multiplikativni_izraz>' or \
            '<aditivni_izraz> MINUS <multiplikativni_izraz>':
        calculate_aditivni_izraz(node.children[0])
        calculate_multiplikativni_izraz(node.children[2])
        temp = productionText.split()[1]
        if temp == 'PLUS':
            node.value = node.children[0].value + node.children[2].value
        elif temp == 'MINUS':
            node.value = node.children[0].value - node.children[2].value
    
def aditivni_izraz(node):
    productionText = getProductionText(node)
    if productionText == '<multiplikativni_izraz>':
        node.children[0].scope = node.scope
        check(node.children[0])

        node.code = node.children[0].code
        node.inc = node.children[0].inc
    elif productionText == '<aditivni_izraz> PLUS <multiplikativni_izraz>' or \
            '<aditivni_izraz> MINUS <multiplikativni_izraz>':
        node.children[0].scope = node.scope
        check(node.children[0])
        node.children[2].scope = node.scope
        check(node.children[2])
        node.code = ''
        if node.children[0].inc:
            node.code = ' PUSH R0\n'
        node.code += node.children[0].code + '\n'
        if node.children[2].inc:
            node.code = ' PUSH R0\n' + node.code
        node.code += node.children[2].code + '\n'
        temp = productionText.split()[1]
        if temp == 'PLUS':
             node.code +=\
                ' POP R0\n' +\
                ' POP R1\n' +\
                ' ADD R1, R0, R0\n' +\
                ' PUSH R0\n' + '\n'
        elif temp == 'MINUS':
            node.code +=\
                ' POP R0\n' + \
                ' POP R1\n' + \
                ' SUB R1, R0, R0\n' + \
                ' PUSH R0\n' + '\n'
        # if not canImplicitlyChange(node.children[0], 'int'):
        #     raise Exception(formatNodeException(node))
        # check(node.children[2])
        # if not canImplicitlyChange(node.children[2], 'int'):
        #     raise Exception(formatNodeException(node))
        # node.type = 'int'
        # node.lExpression = 0

def calculate_odnosni_izraz(node):
    productionText = getProductionText(node)
    if productionText == '<aditivni_izraz>':
        calculate_aditivni_izraz(node.children[0])

        node.value = node.children[0].value
    elif productionText == '<odnosni_izraz> OP_LT <aditivni_izraz>' or \
            '<odnosni_izraz> OP_GT <aditivni_izraz>' or \
            '<odnosni_izraz> OP_LTE <aditivni_izraz>' or \
            '<odnosni_izraz> OP_GTE <aditivni_izraz>':
        calculate_odnosni_izraz(node.children[0])
        calculate_aditivni_izraz(node.children[2])
        temp = productionText.split()[1]
        if temp == 'OP_LT':
            node.value = node.children[0].value < node.children[2].value
        elif temp == 'OP_GT':
            node.value = node.children[0].value > node.children[2].value
        elif temp == 'OP_LTE':
            node.value = node.children[0].value <= node.children[2].value
        elif temp == 'OP_GTE':
            node.value = node.children[0].value <= node.children[2].value

def odnosni_izraz(node):
    global globalLoopNum
    productionText = getProductionText(node)
    if productionText == '<aditivni_izraz>':
        node.children[0].scope = node.scope
        check(node.children[0])

        node.code = node.children[0].code
        node.inc = node.children[0].inc
    elif productionText == '<odnosni_izraz> OP_LT <aditivni_izraz>' or \
            '<odnosni_izraz> OP_GT <aditivni_izraz>' or \
            '<odnosni_izraz> OP_LTE <aditivni_izraz>' or \
            '<odnosni_izraz> OP_GTE <aditivni_izraz>':
        node.children[0].scope = node.scope
        check(node.children[0])
        # if not canImplicitlyChange(node.children[0], 'int'):
        #     raise Exception(formatNodeException(node))
        node.children[2].scope = node.scope
        check(node.children[2])
        # if not canImplicitlyChange(node.children[2], 'int'):
        #     raise Exception(formatNodeException(node))
        # node.type = 'int'
        # node.lExpression = 0
        node.code = ''
        if node.children[0].inc:
            node.code = ' PUSH R0\n'
        node.code += node.children[0].code + '\n'
        if node.children[1].inc:
            node.code = ' PUSH R0\n' + node.code
        node.code += node.children[2].code + '\n'
        tempGlobal = globalLoopNum
        globalLoopNum += 1
        temp = productionText.split()[1]
        if temp == 'OP_LT':
            node.code +=\
                ' POP R1\n' + \
                ' POP R0\n' + \
                ' XOR R2, R2, R2\n' + \
                ' CMP R0, R1\n' + \
                ' JR_SGE l_' + str(tempGlobal) + '\n' +\
                ' ADD R2, 1, R2\n' + \
                'l_' + str(tempGlobal) + '\n' +\
                ' PUSH R2\n'
        elif temp == 'OP_GT':
            node.code +=\
                ' POP R1\n' + \
                ' POP R0\n' + \
                ' XOR R2, R2, R2\n' + \
                ' CMP R0, R1\n' + \
                ' JR_SLE l_' + str(tempGlobal) + '\n' +\
                ' ADD R2, 1, R2\n' + \
                'l_' + str(tempGlobal) + '\n' +\
                ' PUSH R2\n'
        elif temp == 'OP_LTE':
            node.code +=\
                ' POP R1\n' + \
                ' POP R0\n' + \
                ' XOR R2, R2, R2\n' + \
                ' CMP R0, R1\n' + \
                ' JR_SGT l_' + str(tempGlobal) + '\n' +\
                ' ADD R2, 1, R2\n' + \
                'l_' + str(tempGlobal) + '\n' +\
                ' PUSH R2\n'
        elif temp == 'OP_GTE':
            node.code +=\
                ' POP R1\n' + \
                ' POP R0\n' + \
                ' XOR R2, R2, R2\n' + \
                ' CMP R0, R1\n' + \
                ' JR_SLT l_' + str(tempGlobal) + '\n' +\
                ' ADD R2, 1, R2\n' + \
                'l_' + str(tempGlobal) + '\n' +\
                ' PUSH R2\n'

def calculate_jednakosni_izraz(node):
    productionText = getProductionText(node)
    if productionText == '<odnosni_izraz>':
        calculate_odnosni_izraz(node.children[0])

        node.value = node.children[0].value
    elif productionText == '<jednakosni_izraz> OP_EQ <odnosni_izraz>' or \
            '<jednakosni_izraz> OP_NEQ <odnosni_izraz>':
        calculate_jednakosni_izraz(node.children[0])

        calculate_odnosni_izraz(node.children[2])
        if productionText.split()[1] == 'OP_EQ':
            node.value = node.children[0].value == node.children[2].value
        else:
            node.value = node.children[0].value != node.children[2].value

def jednakosni_izraz(node):
    global globalLoopNum
    productionText = getProductionText(node)
    if productionText == '<odnosni_izraz>':
        node.children[0].scope = node.scope
        check(node.children[0])

        node.code = node.children[0].code
        node.inc = node.children[0].inc
    elif productionText == '<jednakosni_izraz> OP_EQ <odnosni_izraz>' or \
            '<jednakosni_izraz> OP_NEQ <odnosni_izraz>':
        node.children[0].scope = node.scope
        check(node.children[0])
        # if not canImplicitlyChange(node.children[0], 'int'):
        #     raise Exception(formatNodeException(node))
        node.children[2].scope = node.scope
        check(node.children[2])
        # if not canImplicitlyChange(node.children[2], 'int'):
        #     raise Exception(formatNodeException(node))
        # node.type = 'int'
        # node.lExpression = 0
        node.code = ''
        if node.children[0].inc:
            node.code = ' PUSH R0\n'
        node.code += node.children[0].code + '\n'
        if node.children[1].inc:
            node.code = ' PUSH R0\n' + node.code
        node.code += node.children[2].code + '\n'
        temp = productionText.split()[1]
        if temp == 'OP_EQ':
            node.code += \
                ' POP R1\n' + \
                ' POP R0\n' + \
                ' XOR R2, R2, R2\n' +\
                ' CMP R1, R0\n' + \
                ' ADD_EQ R2, 1, R2' +\
                ' PUSH R2\n'
        elif temp == 'OP_NEQ':
            node.code += \
                ' POP R1\n' + \
                ' POP R0\n' + \
                ' XOR R2, R2, R2' +\
                ' CMP R1, R0\n' + \
                ' ADD_NE R2, 1, R2\n' +\
                ' PUSH R2\n'

def calculate_bin_i_izraz(node):
    productionText = getProductionText(node)
    if productionText == '<jednakosni_izraz>':
        calculate_jednakosni_izraz(node.children[0])

        node.value = node.children[0].value
    elif productionText == '<bin_i_izraz> OP_BIN_I <jednakosni_izraz>':
        check(node.children[0])
        node.value = node.children[0].value
        calculate_jednakosni_izraz(node.children[2])
        node.value = node.value & node.children[2].value

def bin_i_izraz(node):
    productionText = getProductionText(node)
    if productionText == '<jednakosni_izraz>':
        node.children[0].scope = node.scope
        check(node.children[0])

        node.code = node.children[0].code
        node.inc = node.children[0].inc
    elif productionText == '<bin_i_izraz> OP_BIN_I <jednakosni_izraz>':
        node.children[0].scope = node.scope
        check(node.children[0])
        # if not canImplicitlyChange(node.children[0], 'int'):
        #     raise Exception(formatNodeException(node))
        node.children[2].scope = node.scope
        check(node.children[2])
        # if not canImplicitlyChange(node.children[2], 'int'):
        #     raise Exception(formatNodeException(node))
        # node.type = 'int'
        # node.lExpression = 0
        node.code = ''
        if node.children[0].inc:
            node.code = ' PUSH R0\n'
        node.code += node.children[0].code + '\n'
        if node.children[1].inc:
            node.code = ' PUSH R0\n' + node.code
        node.code += node.children[2].code + '\n'
        node.code += \
            ' POP R0\n' + \
            ' POP R1\n' + \
            ' AND R0, R1, R0\n' + \
            ' PUSH R0\n'

def calculate_bin_xili_izraz(node):
    productionText = getProductionText(node)
    if productionText == '<bin_i_izraz>':
        calculate_bin_i_izraz(node.children[0])

        node.value = node.children[0].value
    elif productionText == '<bin_xili_izraz> OP_BIN_XILI <bin_i_izraz>':
        calculate_bin_xili_izraz(node.children[0])
        node.value = node.children[0].value
        calculate_bin_i_izraz(node.children[2])
        node.value = node.value ^ node.children[2].value

def bin_xili_izraz(node):
    productionText = getProductionText(node)
    if productionText == '<bin_i_izraz>':
        node.children[0].scope = node.scope
        check(node.children[0])

        node.code = node.children[0].code
        node.inc = node.children[0].inc
    elif productionText == '<bin_xili_izraz> OP_BIN_XILI <bin_i_izraz>':
        node.children[0].scope = node.scope
        check(node.children[0])
        # if not canImplicitlyChange(node.children[0], 'int'):
        #     raise Exception(formatNodeException(node))
        node.children[2].scope = node.scope
        check(node.children[2])
        # if not canImplicitlyChange(node.children[2], 'int'):
        #     raise Exception(formatNodeException(node))
        # node.type = 'int'
        # node.lExpression = 0
        node.code = ''
        if node.children[0].inc:
            node.code = ' PUSH R0\n'
        node.code += node.children[0].code + '\n'
        if node.children[1].inc:
            node.code = ' PUSH R0\n' + node.code
        node.code += node.children[2].code + '\n'
        node.code +=\
            ' POP R0\n' + \
            ' POP R1\n' + \
            ' XOR R0, R1, R0\n' + \
            ' PUSH R0\n'

def calculate_bin_ili_izraz(node):
    productionText = getProductionText(node)
    if productionText == '<bin_xili_izraz>':
        calculate_bin_xili_izraz(node.children[0])

        node.value = node.children[0].value
    elif productionText == '<bin_ili_izraz> OP_BIN_ILI <bin_xili_izraz>':
        calculate_bin_ili_izraz(node.children[0])
        node.value = node.children[0].value
        calculate_bin_xili_izraz(node.children[2])
        node.value = node.value | node.children[2].value

def bin_ili_izraz(node):
    productionText = getProductionText(node)
    if productionText == '<bin_xili_izraz>':
        node.children[0].scope = node.scope
        check(node.children[0])

        node.code = node.children[0].code
        node.inc = node.children[0].inc
    elif productionText == '<bin_ili_izraz> OP_BIN_ILI <bin_xili_izraz>':
        node.children[0].scope = node.scope
        check(node.children[0])
        # if not canImplicitlyChange(node.children[0], 'int'):
        #     raise Exception(formatNodeException(node))
        node.children[2].scope = node.scope
        check(node.children[2])
        # if not canImplicitlyChange(node.children[2], 'int'):
        #     raise Exception(formatNodeException(node))
        # node.type = 'int'
        # node.lExpression = 0
        node.code = ''
        if node.children[0].inc:
            node.code = ' PUSH R0\n'
        node.code += node.children[0].code + '\n'
        if node.children[1].inc:
            node.code = ' PUSH R0\n' + node.code
        node.code += node.children[2].code + '\n'
        node.code +=\
            ' POP R0\n' +\
            ' POP R1\n' +\
            ' OR R0, R1, R0\n' +\
            ' PUSH R0\n'

def calculate_log_i_izraz(node):
    productionText = getProductionText(node)
    if productionText == '<bin_ili_izraz>':
        calculate_bin_ili_izraz(node.children[0])

        node.value = node.children[0].value
    elif productionText == '<log_i_izraz> OP_I <bin_ili_izraz>':
        calculate_log_i_izraz(node.children[0])
        node.value = node.children[0].value
        # if not canImplicitlyChange(node.children[0], 'int'):
        #     raise Exception(formatNodeException(node))
        if node.value:
            calculate_bin_ili_izraz(node.children[2])
            node.value = node.value and node.children[2].value
        # if not canImplicitlyChange(node.children[2], 'int'):
        #     raise Exception(formatNodeException(node))
        # node.type = 'int'
        # node.lExpression = 0

def log_i_izraz(node):
    global globalLoopNum
    productionText = getProductionText(node)
    if productionText == '<bin_ili_izraz>':
        node.children[0].scope = node.scope
        check(node.children[0])

        node.code = node.children[0].code
        node.inc = node.children[0].inc
    elif productionText == '<log_i_izraz> OP_I <bin_ili_izraz>':
        node.children[0].scope = node.scope
        check(node.children[0])
        # if not canImplicitlyChange(node.children[0], 'int'):
        #     raise Exception(formatNodeException(node))
        node.children[2].scope = node.scope
        check(node.children[2])
        # if not canImplicitlyChange(node.children[2], 'int'):
        #     raise Exception(formatNodeException(node))
        # node.type = 'int'
        # node.lExpression = 0
        temp = globalLoopNum
        globalLoopNum += 2
        node.code = ''

        if node.children[0].inc:
            node.code = ' PUSH R0\n'
        node.code += node.children[0].code + '\n' + \
            ' XOR R0, R0, R0\n' + \
            ' POP R1\n' + \
            ' CMP R1, R0\n' + \
            ' JR_EQ  l_' + str(temp) + '\n\n'
        if node.children[1].inc:
            node.code = ' PUSH R0\n' + node.code
        node.code += node.children[2].code + '\n' + \
            ' XOR R0, R0, R0\n' + \
            ' POP R1\n' + \
            ' CMP R1, R0\n' + \
            ' JR_EQ  l_' + str(temp) + '\n' + \
            ' ADD R0, 1, R0\n' +\
            ' PUSH R0\n' + \
            ' JR l_' + str(temp + 1) + '\n' + \
            'l_' + str(temp) + \
            ' PUSH R0\n' + \
            'l_' + str(temp + 1) + '\n'

def calculate_log_ili_izraz(node):
    productionText = getProductionText(node)
    if productionText == '<log_i_izraz>':
        calculate_log_i_izraz(node.children[0])

        node.value = node.children[0].value
    elif productionText == '<log_ili_izraz> OP_ILI <log_i_izraz>':
        calculate_log_ili_izraz(node.children[0])
        node.value = node.children[0].value
        # if not canImplicitlyChange(node.children[0], 'int'):
        #     raise Exception(formatNodeException(node))
        if not node.value:
            calculate_log_i_izraz(node.children[2])
            node.value = node.value or node.children[2].value
        # if not canImplicitlyChange(node.children[2], 'int'):
        #     raise Exception(formatNodeException(node))
        # node.type = 'int'
        # node.lExpression = 0

def log_ili_izraz(node):
    global globalLoopNum
    productionText = getProductionText(node)
    if productionText == '<log_i_izraz>':
        node.children[0].scope = node.scope
        check(node.children[0])

        node.code = node.children[0].code
        node.inc = node.children[0].inc
    elif productionText == '<log_ili_izraz> OP_ILI <log_i_izraz>':
        node.children[0].scope = node.scope
        check(node.children[0])
        # if not canImplicitlyChange(node.children[0], 'int'):
        #     raise Exception(formatNodeException(node))
        node.children[2].scope = node.scope
        check(node.children[2])
        # if not canImplicitlyChange(node.children[2], 'int'):
        #     raise Exception(formatNodeException(node))
        # node.type = 'int'
        # node.lExpression = 0
        temp = globalLoopNum
        globalLoopNum += 2
        node.code = ''

        if node.children[0].inc:
            node.code = ' PUSH R0\n'
        node.code += node.children[0].code + '\n' +\
            ' XOR R0, R0, R0\n' +\
            ' POP R1\n' +\
            ' CMP R1, R0\n' +\
            ' JR_NE  l_' + str(temp) + '\n\n'
        if node.children[1].inc:
            node.code = ' PUSH R0\n' + node.code
        node.code += node.children[2].code + '\n' + \
            ' XOR R0, R0, R0\n' + \
            ' POP R1\n' + \
            ' CMP R1, R0\n' + \
            ' JR_NE  l_' + str(temp) + '\n' +\
            ' PUSH R0\n' +\
            ' JR l_' + str(temp+1) + '\n' +\
            'l_' + str(temp) +\
            ' ADD R0, 1, R0\n' + \
            ' PUSH R0\n' + \
            'l_' + str(temp+1) + '\n'

def calculate_izraz_pridruzivanja(node):
    productionText = getProductionText(node)
    if productionText == '<log_ili_izraz>':
        # node.children[0].type = node.type
        calculate_log_ili_izraz(node.children[0])
        node.value = node.children[0].value
    elif productionText == '<postfiks_izraz> OP_PRIDRUZI <izraz_pridruzivanja>':
        raise Exception('calculate ima pridruzi')

def izraz_pridruzivanja(node):
    productionText = getProductionText(node)
    if productionText == '<log_ili_izraz>':
        node.children[0].scope = node.scope
        check(node.children[0])

        node.code = node.children[0].code
        node.inc = node.children[0].inc
    elif productionText == '<postfiks_izraz> OP_PRIDRUZI <izraz_pridruzivanja>':
        node.children[0].scope = node.scope
        check(node.children[0])
        # if not node.children[0].lExpression == 1:
        #     raise Exception(formatNodeException(node))
        node.children[2].scope = node.scope
        check(node.children[2])
        # if not canImplicitlyChange(node.children[2], node.children[0]):
        #     raise Exception(formatNodeException(node))
        # node.type = node.children[0].type
        # node.lExpression = 0
        node.code = ''

        if node.children[0].inc:
            node.children[0].code = node.children[0].code + ' PUSH R0\n'
        if node.children[2].inc:
            node.children[2].code = node.children[2].code + ' PUSH R0\n'

        if node.children[0].elemNum != None:
            node.code = node.children[0].elemNum + '\n'
        else:
            node.code = ' MOVE 0, R0\n' +\
                ' PUSH R0\n'
        node.code += \
            node.children[2].code + '\n' +\
            ' POP R0\n' +\
            saveVarCode(node.children[0].code, node.scope, 'R0', 'R3') + '\n PUSH R0\n'

def izraz(node):
    productionText = getProductionText(node)
    if productionText == '<izraz_pridruzivanja>':
        node.children[0].scope = node.scope
        check(node.children[0])

        node.code = node.children[0].code

        node.inc = node.children[0].inc
    elif productionText == '<izraz> ZAREZ <izraz_pridruzivanja>':
        node.children[0].scope = node.scope
        check(node.children[0])
        node.children[2].scope = node.scope
        check(node.children[2])
        # node.type = node.children[2].type
        # node.lExpression = 0
        if node.children[0].inc:
            node.children[0].code = node.children[0].code + ' PUSH R0\n'
        if node.children[2].inc:
            node.children[2].code = node.children[2].code + ' PUSH R0\n'
        node.code =\
            node.children[0].code + '\n' +\
            ' POP R0\n' + \
            node.children[2].code + '\n'

def slozena_naredba(node):
    productionText = getProductionText(node)
    if productionText == 'L_VIT_ZAGRADA <lista_naredbi> D_VIT_ZAGRADA':
        node.children[1].scope = node.scope + [[]]
        node.children[1].lStart = node.lStart
        node.children[1].lEnd = node.lEnd
        check(node.children[1])

        node.code = node.children[1].code
    elif productionText == 'L_VIT_ZAGRADA <lista_deklaracija> <lista_naredbi> D_VIT_ZAGRADA':
        node.children[1].scope = node.scope + [[]]
        check(node.children[1])
        node.children[2].lStart = node.lStart
        node.children[2].lEnd = node.lEnd
        node.children[2].scope = node.children[1].scope
        check(node.children[2])
        # node.code = node.children[2].code + '\n' + \
        #         ' POP R0\n' * node.children[1].elemNum
        node.code = node.children[1].code + '\n' + node.children[2].code + '\n' +\
            ' POP R0\n' * node.children[1].elemNum

def lista_naredbi(node):
    productionText = getProductionText(node)
    if productionText == '<naredba>':
        node.children[0].scope = node.scope
        node.children[0].lStart = node.lStart
        node.children[0].lEnd = node.lEnd
        check(node.children[0])
        # node.scope = node.children[0].scope

        node.code = node.children[0].code
    elif productionText == '<lista_naredbi> <naredba>':
        node.children[0].scope = node.scope
        node.children[0].lStart = node.lStart
        node.children[0].lEnd = node.lEnd
        check(node.children[0])
        node.children[1].scope = node.scope
        node.children[1].lStart = node.lStart
        node.children[1].lEnd = node.lEnd
        check(node.children[1])
        node.code = node.children[0].code + '\n' + node.children[1].code

def naredba(node):
    node.children[0].scope = node.scope
    node.children[0].lStart = node.lStart
    node.children[0].lEnd = node.lEnd
    check(node.children[0])

    node.code = node.children[0].code

def izraz_naredba(node):
    productionText = getProductionText(node)
    if productionText == 'TOCKAZAREZ':
        node.type = 'int'
        node.code = ''
    elif productionText == '<izraz> TOCKAZAREZ':
        node.children[0].scope = node.scope
        check(node.children[0])
        node.type = node.children[0].type
        node.code = node.children[0].code + '\n POP R0\n'

def naredba_grananja(node):
    global globalLoopNum
    productionText = getProductionText(node)
    if productionText == 'KR_IF L_ZAGRADA <izraz> D_ZAGRADA <naredba>':
        node.children[2].scope = node.scope
        check(node.children[2])
        # if not canImplicitlyChange(node.children[2], 'int'):
        #     raise Exception(formatNodeException(node))
        node.children[4].scope = node.scope
        node.children[4].lStart = node.lStart
        node.children[4].lEnd = node.lEnd
        check(node.children[4])

        temp = globalLoopNum
        globalLoopNum += 1

        node.code = \
            node.children[2].code + '\n' + \
            ' POP R0\n' + \
            ' MOVE 0, R1\n' + \
            ' CMP R0, R1\n' + \
            ' JP_EQ l_' + str(temp) + '\n\n' + \
            node.children[4].code + '\n' + \
            'l_' + str(temp) + '\n'

    if productionText == 'KR_IF L_ZAGRADA <izraz> D_ZAGRADA <naredba> KR_ELSE <naredba>':
        node.children[2].scope = node.scope
        check(node.children[2])
        # if not canImplicitlyChange(node.children[2], 'int'):
        #     raise Exception(formatNodeException(node))
        node.children[4].scope = node.scope
        node.children[4].lStart = node.lStart
        node.children[4].lEnd = node.lEnd
        check(node.children[4])
        node.children[6].scope = node.scope
        node.children[6].lStart = node.lStart
        node.children[6].lEnd = node.lEnd
        check(node.children[6])

        temp = globalLoopNum
        globalLoopNum += 2

        node.code =\
            node.children[2].code + '\n' +\
            ' POP R0\n' +\
            ' MOVE 0, R1\n' +\
            ' CMP R0, R1\n' +\
            ' JP_EQ l_' + str(temp) + '\n\n' +\
            node.children[4].code + '\n' +\
            ' JP l_' + str(temp+1) + '\n' +\
            'l_' + str(temp) + '\n\n' +\
            node.children[6].code + '\n' + \
            'l_' + str(temp + 1) + '\n'

def naredba_petlje(node):
    global globalLoopNum
    productionText = getProductionText(node)
    if productionText == 'KR_WHILE L_ZAGRADA <izraz> D_ZAGRADA <naredba>':
        node.children[2].scope = node.scope
        check(node.children[2])
        # if not canImplicitlyChange(node.children[2], 'int'):
        #     raise Exception(formatNodeException(node))
        temp = globalLoopNum
        globalLoopNum += 2
        node.children[4].scope = node.children[2].scope
        node.children[4].lStart = temp
        node.children[4].lEnd = temp+1
        check(node.children[4])
        node.code =\
            'l_' + str(temp) + '\n\n' +\
            node.children[2].code + '\n' +\
            ' POP R0\n' +\
            ' MOVE 0, R1\n' +\
            ' CMP R0, R1\n' +\
            ' JP_EQ l_' + str(temp+1) + '\n\n' +\
            node.children[4].code + '\n' +\
            ' JP l_' + str(temp) + '\n' +\
            'l_' + str(temp+1) + '\n'
    elif productionText == 'KR_FOR L_ZAGRADA <izraz_naredba> <izraz_naredba> D_ZAGRADA <naredba>':
        node.children[2].scope = node.scope
        check(node.children[2])
        node.children[3].scope = node.children[2].scope
        check(node.children[3])
        # if not canImplicitlyChange(node.children[3], 'int'):
        #     raise Exception(formatNodeException(node))
        temp = globalLoopNum
        globalLoopNum += 2
        node.children[5].scope = node.children[3].scope
        node.children[5].lStart = temp
        node.children[5].lEnd = temp+1
        check(node.children[5])
        node.code = \
            node.children[2].code + '\n' +\
            'l_' + str(temp) + '\n\n' + \
            node.children[3].code + '\n' + \
            ' POP R0\n' +\
            ' MOVE 0, R1\n' +\
            ' CMP R0, R1\n' +\
            ' JP_EQ l_' + str(temp+1) + '\n\n' + \
            node.children[5].code + '\n' + \
            ' JP l_' + str(temp) + '\n' +\
            'l_' + str(temp+1) + '\n'
    elif productionText == 'KR_FOR L_ZAGRADA <izraz_naredba> <izraz_naredba> <izraz> D_ZAGRADA <naredba>':
        node.children[2].scope = node.scope
        check(node.children[2])
        node.children[3].scope = node.children[2].scope
        check(node.children[3])
        # if not canImplicitlyChange(node.children[3], 'int'):
        #     raise Exception(formatNodeException(node))
        node.children[4].scope = node.children[3].scope
        check(node.children[4])
        temp = globalLoopNum
        globalLoopNum += 2
        node.children[6].scope = node.children[4].scope
        node.children[6].lStart = temp
        node.children[6].lEnd = temp+1
        check(node.children[6])
        node.code = \
            node.children[2].code + '\n' + \
            'l_' + str(temp) + '\n\n' + \
            node.children[3].code + '\n' + \
            ' PUSH R0\n' +\
            ' POP R0\n' + \
            ' MOVE 0, R1\n' + \
            ' CMP R0, R1\n' + \
            ' JP_EQ l_' + str(temp + 1) + '\n\n' + \
            node.children[6].code + '\n' + \
            node.children[4].code + '\n' +\
            ' POP R0\n' +\
            ' JP l_' + str(temp) + '\n' + \
            'l_' + str(temp + 1) + '\n'


# def isInLoop(node):
#     if node.parent == None:
#         return False
#     elif node.parent.content == '<naredba_petlje>':
#         return True
#     else:
#         return isInLoop(node.parent)
#
# def isInFunction(node):
#     if node.parent == None:
#         return False
#     elif node.parent.content == '<definicija_funkcije>':
#         return node.parent.children[0].type
#     else:
#         return isInLoop(node.parent)

def naredba_skoka(node):
    productionText = getProductionText(node)
    if productionText == 'KR_CONTINUE TOCKAZAREZ' or \
            productionText == 'KR_BREAK TOCKAZAREZ':
        temp = productionText.split()[0]
        if temp == 'KR_CONTINUE':
            node.code = ' JP l_' + str(node.lStart) + '\n'
        elif temp == 'KR_BREAK':
            node.code = ' JP l_' + str(node.lEnd) + '\n'
        # if not isInLoop(node):
        #     raise Exception(formatNodeException(node))
    elif productionText == 'KR_RETURN TOCKAZAREZ':
        node.children[1].scope = node.scope
        check(node.children[1])

        size = 0


        for i in node.scope[1:]:
            for j in i:
                size += j[1]

        node.code = node.children[1].code + \
            ' POP R0\n' * size +\
            ' RET\n'
        # if isInFunction(node) != 'void':
        #     raise Exception(formatNodeException(node))
    elif productionText == 'KR_RETURN <izraz> TOCKAZAREZ':
        if node.children[1].inc:
            node.children[1].code = node.children[1].code + ' PUSH R0\n'
        node.children[1].scope = node.scope
        check(node.children[1])

        size = 0

        for i in node.scope[1:]:
            for j in i:
                size += j[1]

        node.code = node.children[1].code + \
            ' POP R6\n' + \
            ' POP R0\n' * size +\
            ' RET\n'

def prijevodna_jedinica(node):
    productionText = getProductionText(node)
    if productionText == '<vanjska_deklaracija>':
        check(node.children[0])
        node.code = node.children[0].code
    elif productionText == '<prijevodna_jedinica> <vanjska_deklaracija>':
        node.children[0].scope = node.scope
        check(node.children[0])
        node.children[1].scope = node.scope
        check(node.children[1])
        if node.children[0].code != None:
            node.code = node.children[0].code +\
                '\n' +\
                node.children[1].code
        else:
            node.code = node.children[1].code

def vanjska_deklaracija(node):
    productionText = getProductionText(node)
    if productionText == '<deklaracija>':
        node.children[0].scope = node.scope
        check(node.children[0])
    else:
        node.children[0].scope = node.scope
        check(node.children[0])
        node.code = node.children[0].code

def define(name):
    # print(name)
    rootNode.characterTable[name]['defined'] = True

def isDefined(name):
    if name not in rootNode.characterTable.keys():
        return False
    return rootNode.characterTable[name]['defined']

def declare(node, name, type, lExpression):
    # print(name)
    if node.characterTable == None:
        declare(findScopeNode(node), name, type, lExpression)
    else:
        node.characterTable[name]['lExpression'] = lExpression
        node.characterTable[name]['declared'] = True
        node.characterTable[name]['type'] = type

# def getFuncType(name):
#     declaredInNode(node, name).characterTable[name]['type']

def definicija_funkcije(node):
    productionText = getProductionText(node)
    if productionText == '<ime_tipa> IDN L_ZAGRADA KR_VOID D_ZAGRADA <slozena_naredba>':
        check(node.children[0])
        node.children[5].scope = [[]]
        check(node.children[5])

        node.code = \
            'f_' + getCharacterName(node.children[1].content) + '\n' +\
            node.children[5].code +\
            ' RET\n'
        # if isConst(node.children[0].type):
        #     raise Exception(formatNodeException(node))
        # if isDefined(getCharacterName(node.children[1].content)):
        #     raise Exception(formatNodeException(node))
        # if getCharacterName(node.children[1].content) in rootNode.characterTable:
        #     if not rootNode.characterTable[getCharacterName(node.children[1].content)]['type'] == \
        #         'funkcija(void → ' + node.children[0].type + ')':
        #             raise Exception(formatNodeException(node))
        # declare(node, getCharacterName(node.children[1].content), node.children[0].type, node.children[1].lExpression)
        # define(getCharacterName(node.children[1].content))
        # node.characterTable = node.children[5].characterTable
        # check(node.children[5])
    elif productionText == '<ime_tipa> IDN L_ZAGRADA <lista_parametara> D_ZAGRADA <slozena_naredba>':
        check(node.children[0])
        # if isConst(node.children[0].type):
        #     raise Exception(formatNodeException(node))
        # if isDefined(getCharacterName(node.children[1].content)):
        #     raise Exception(formatNodeException(node))
        node.children[3].scope = [[]]
        check(node.children[3])
        # if getCharacterName(node.children[1].content) in rootNode.characterTable:
        #     if not rootNode.characterTable[getCharacterName(node.children[1].content)]['type'] == \
        #         'funkcija(void → ' + node.children[0].type + ')':
        #             raise Exception(formatNodeException(node))
        # declare(node, getCharacterName(node.children[1].content), node.children[0].type, node.children[1].lExpression)
        # define(getCharacterName(node.children[1].content))
        # for i in range(node.children[3]):
        #     declare(node, node.children[3].names[i], node.children[3].type[i], None) # iupitno
        # node.characterTable = node.children[5].characterTable
        node.children[5].scope = node.children[3].scope
        check(node.children[5])

        node.code = \
            'f_' + getCharacterName(node.children[1].content) + '\n' + \
            node.children[5].code +\
            ' RET\n'

def lista_parametara(node):
    productionText = getProductionText(node)
    if productionText == '<deklaracija_parametra>':
        node.children[0].scope = node.scope
        check(node.children[0])
        node.scope = node.children[0].scope
        # node.type = [node.children[0].type]
        # node.names = [getCharacterName(node.children[0].content)]
    elif productionText == '<lista_parametara> ZAREZ <deklaracija_parametra>':
        node.children[0].scope = node.scope
        check(node.children[0])
        node.children[2].scope = node.children[0].scope
        check(node.children[2])
        node.scope = node.children[0].scope
        # if getCharacterName(node.children[0].content) in node.children[0].names:
        #     raise Exception(formatNodeException(node))
        # node.type = node.children[0].type + [node.children[2].type]
        # node.names = node.children[0].names + [getCharacterName(node.children[2].content)]
        
def deklaracija_parametra(node):
    productionText = getProductionText(node)
    if productionText == '<ime_tipa> IDN':
        check(node.children[0])
        # if node.children[0].type == 'void':
        #     raise Exception(formatNodeException(node))
        # node.type = node.children[0].type
        # node.names = getCharacterName(node.children[1].content)
        node.scope[-1] += [[getCharacterName(node.children[1].content), 1]]
    elif productionText == '<ime_tipa> IDN L_UGL_ZAGRADA D_UGL_ZAGRADA':
        check(node.children[0])
        # if node.children[0].type == 'void':
        #     raise Exception(formatNodeException(node))
        # node.type = 'niz(' + node.children[0].type + ')'
        # node.names = getCharacterName(node.children[1].content)
        node.scope[-1] += [[getCharacterName(node.children[1].content), 1, 'pointer']]

def lista_deklaracija(node):
    productionText = getProductionText(node)
    if productionText == '<deklaracija>':
        node.elemNum = 1
        node.children[0].scope = node.scope
        check(node.children[0])
        node.scope = node.children[0].scope
        node.code = node.children[0].code + '\n'
    elif productionText == '<lista_deklaracija> <deklaracija>':
        node.children[0].scope = node.scope
        check(node.children[0])
        node.children[1].scope = node.children[0].scope
        check(node.children[1])
        node.scope = node.children[1].scope
        node.code = node.children[0].code + '\n' + node.children[1].code
        node.elemNum = node.children[0].elemNum + 1

def deklaracija(node):
    global globalCode
    productionText = getProductionText(node)
    if productionText == '<ime_tipa> <lista_init_deklaratora> TOCKAZAREZ':
        if node.scope != None:
            node.children[0].scope = node.scope
            check(node.children[0])
            node.children[1].type = node.children[0].type
            node.children[1].scope = node.children[0].scope
            check(node.children[1])
            node.scope = node.children[1].scope
            node.code = node.children[1].code
        else:
            check(node.children[0])
            node.children[1].type = node.children[0].type
            calculate_lista_init_deklaratora(node.children[1])
            globalCode += '\n' + node.children[1].code

def calculate_lista_init_deklaratora(node):
    global globalCode
    productionText = getProductionText(node)
    if productionText == '<init_deklarator>':
        node.children[0].type = node.type
        calculate_init_deklarator(node.children[0])
        node.code = node.children[0].code
    elif productionText == '<lista_init_deklaratora> ZAREZ <init_deklarator>':
        raise Exception('calculate_lista_izraza_pridruzivanja' + productionText)
        # node.children[0].type = node.type
        # calculate_lista_init_deklaratora(node.children[0])
        # node.children[2].type = node.type
        # calculate_init_deklarator(node.children[2])
        # node.code = node.children[0].code +\
        #             '\n'+\
        #             node.children[1].code

def lista_init_deklaratora(node):
    productionText = getProductionText(node)
    if productionText == '<init_deklarator>':
        # node.children[0].ntype = node.ntype
        node.children[0].scope = node.scope
        check(node.children[0])
        node.scope = node.children[0].scope
        node.code = node.children[0].code
    elif productionText == '<lista_init_deklaratora> ZAREZ <init_deklarator>':
        # node.children[0].ntype = node.ntype
        node.children[0].scope = node.scope
        check(node.children[0])
        # node.children[2].ntype = node.ntype
        node.children[2].scope = node.children[0].scope
        check(node.children[2])
        node.scope = node.children[0].scope
        node.code = node.children[0].code + '\n' + node.children[2].code

def calculate_init_deklarator(node):
    productionText = getProductionText(node)
    if productionText == '<izravni_deklarator>':
        node.children[0].type = node.type
        calculate_izravni_deklarator(node.children[0])
        # node.code = 'g_' + node.children[0].name + ' ' + 'DW %D ' + \
        #             ', '.join([0 for i in range(node.children[0].size)]) + '\n'
        node.code = \
            'g_' + node.children[0].code + ' DW %D ' +\
            ', %D '.join(['0' for i in range(node.children[0].size)]) + '\n' + \
            '\n'

    elif productionText == '<izravni_deklarator> OP_PRIDRUZI <inicijalizator>':
        node.children[0].type = node.type
        calculate_izravni_deklarator(node.children[0])
        node.children[2].type = node.type
        calculate_inicijalizator(node.children[2])
        if not isinstance(node.children[2].value, int):
            # for i in range(node.children[0].size):
            #     if i < len(node.children[2].value):
            #         node.code +=\
            #             'g_' + node.children[0].name + ' ' + 'DW %D ' + node.children[2].value[i] + '\n' +\
            #             '\n'
            #     else:
            #         node.code += \
            #             'g_' + i + '_' + node.children[0].name + ' ' + 'DW %D 0\n' + \
            #             '\n'
            node.code = \
                'g_' + node.children[0].code + ' ' + 'DW %D ' + \
                ', %D '.join([str(v) for v in node.children[2].value]) + \
                ', %D '.join(['0' for i in range(node.children[0].size - len(node.children[2].value))]) + \
                '\n'
        else:
            # node.code = 'g_0_' + node.children[0].name + ' ' + 'DW %D ' + \
            #             str(node.children[2].value) + '\n'
            node.code = \
                'g_' + node.children[0].code + ' ' + 'DW %D ' + \
                str(node.children[2].value) + '\n'

        # if len(node.children[0].value) > 1:
        #     node.code = ','.join(node.children[0].value) + ', 0'
        # else:
        #     node.code = str(node.children[0].value)

def init_deklarator(node):
    productionText = getProductionText(node)
    if productionText == '<izravni_deklarator>':
        node.children[0].scope = node.scope
        check(node.children[0])
        if node.children[0].decodeType != Node.decodeType.FUNC:
            node.scope[-1] += [[node.children[0].code, node.children[0].elemNum]]
        node.code = \
            ' XOR R0, R0, R0\n' +\
            ' PUSH R0\n' *  node.children[0].elemNum
    elif productionText == '<izravni_deklarator> OP_PRIDRUZI <inicijalizator>':
        node.children[0].scope = node.scope
        check(node.children[0])
        node.children[2].scope = node.scope
        check(node.children[2])
        if node.children[0].decodeType != Node.decodeType.FUNC:
            node.scope[-1] += [[node.children[0].code, node.children[0].elemNum]]
        node.code = \
            node.children[2].code + '\n' +\
            ' XOR R0, R0, R0\n' + \
            ' PUSH R0\n' * (node.children[0].elemNum - node.children[2].elemNum)


def calculate_izravni_deklarator(node):
    global globalScope
    productionText = getProductionText(node)
    if productionText == 'IDN':
        # if node.ntype == 'void':
        #     raise Exception(formatNodeException(node))
        node.code = getCharacterName(node.children[0].content)
        node.size = 1
        globalScope += [[node.code, node.size]]
        # if declaredInNode(node, name) == node.scopeNode:
        #     raise Exception(formatNodeException(node))
        # declare(node.scopeNode, name, node.ntype, node.children[0].lExpression)
        # node.type = node.ntype
    elif productionText == 'IDN L_UGL_ZAGRADA BROJ D_UGL_ZAGRADA':
        # if node.ntype == 'void':
        #     raise Exception(formatNodeException(node))
        node.code = getCharacterName(node.children[0].content)
        # if declaredInNode(node, name) == node.scopeNode:
        #     raise Exception(formatNodeException(node))
        # if not (isInt(getCharacterName(name)) and \
        #         int(getCharacterName(name)) > 0 and \
        #         int(getCharacterName(name)) <= 1024):
        #     raise Exception(formatNodeException(node))
        # declare(node.scopeNode, name, 'niz(' + node.ntype + ')', node.children[0].lExpression)
        # node.type = node.ntype
        node.size = int(getCharacterName(node.children[2].content))
        globalScope += [[node.code, node.size]]

def izravni_deklarator(node):
    productionText = getProductionText(node)
    if productionText == 'IDN':
        # if node.ntype == 'void':
        #     raise Exception(formatNodeException(node))
        node.code = getCharacterName(node.children[0].content)
        # if declaredInNode(node, name) == node.scopeNode:
        #     raise Exception(formatNodeException(node))
        # declare(node.scopeNode, name, node.ntype, node.children[0].lExpression)
        # node.type = node.ntype
        node.elemNum = 1
        node.decodeType = Node.decodeType.VAR
    elif productionText == 'IDN L_UGL_ZAGRADA BROJ D_UGL_ZAGRADA':
        # if node.ntype == 'void':
        #     raise Exception(formatNodeException(node))
        node.code = getCharacterName(node.children[0].content)
        # if declaredInNode(node, name) == node.scopeNode:
        #     raise Exception(formatNodeException(node))
        # if not (isInt(getCharacterName(name)) and \
        #     int(getCharacterName(name)) > 0 and \
        #     int(getCharacterName(name)) <= 1024):
        #     raise Exception(formatNodeException(node))
        # declare(node.scopeNode, name, 'niz(' + node.ntype + ')', node.children[0].lExpression)
        # node.type = node.ntype
        # node.elemNum = int(getCharacterName(node.children[2].content))
        node.elemNum = int(getCharacterName(node.children[2].content))
        node.decodeType = Node.decodeType.STR
    elif productionText == 'IDN L_ZAGRADA KR_VOID D_ZAGRADA':
        node.decodeType = Node.decodeType.FUNC
        # name = getCharacterName(node.children[0].content)
        # if declaredInNode(node, name) == node.scopeNode:
        #     if not declaredInNode(node, name).type == 'funkcija(void → ' + node.ntype + ')':
        #         raise Exception(formatNodeException(node))
        # else:
        #     declare(node.scopeNode, name, 'funkcija(void → ' + node.ntype + ')', node.children[0].lExpression)
        # node.type = 'funkcija(void → ' + node.ntype + ')'
    elif productionText == 'IDN L_ZAGRADA <lista_parametara> D_ZAGRADA':
        node.decodeType = Node.decodeType.FUNC
        # check(node.children[2])
        # name = getCharacterName(node.children[0].content)
        # if declaredInNode(node, name) == node.scopeNode:
        #     if not declaredInNode(node, name).type == 'funkcija(' + ' '.join(node.children[2]) + ' → ' + node.ntype + ')':
        #         raise Exception(formatNodeException(node))
        # else:
        #     declare(node.scopeNode, name, 'funkcija(' + ' '.join(node.children[2]) + ' → ' + node.ntype + ')', node.children[0].lExpression)
        # node.type = 'funkcija(' + ' '.join(node.children[2]) + ' → ' + node.ntype + ')'

def leadsTo(node, name):
    val = False
    for child in node.children:
        if getCharacterUniformName(child)[0] != '<':
            if getCharacterUniformName(child) == 'NIZ_ZNAKOVA':
                return getCharacterName(child)
            else:
                return False
        else:
            val = leadsTo(child, name)
    return val

def calculate_inicijalizator(node):
    productionText = getProductionText(node)
    if productionText == '<izraz_pridruzivanja>':
        node.children[0].type = node.type
        calculate_izraz_pridruzivanja(node.children[0])
        node.value = node.children[0].value
        # if leadsTo(node, 'NIZ_ZNAKOVA') != False:
        #     node.elemNum = len(leadsTo(node, 'NIZ_ZNAKOVA')) + 1
        #     node.type = ['char'] * node.elemNum
        # else:
        #     node.type = node.children[0].type
    elif productionText == 'L_VIT_ZAGRADA <lista_izraza_pridruzivanja> D_VIT_ZAGRADA':
        node.children[1].type = node.type
        calculate_lista_izraza_pridruzivanja(node.children[1])
        node.elemNum = node.children[1].elemNum
        node.value = node.children[1].value

def inicijalizator(node):
    productionText = getProductionText(node)
    if productionText == '<izraz_pridruzivanja>':
        node.children[0].scope = node.scope
        check(node.children[0])
        # if leadsTo(node, 'NIZ_ZNAKOVA') != False:
        #     node.elemNum = len(leadsTo(node, 'NIZ_ZNAKOVA')) + 1
        #     node.type = ['char'] * node.elemNum
        # else:
        #     node.type = node.children[0].type
        node.elemNum = 1
        node.code = node.children[0].code
        if node.children[0].inc:
            node.code += ' PUSH R0\n'
    elif productionText == 'L_VIT_ZAGRADA <lista_izraza_pridruzivanja> D_VIT_ZAGRADA':
        node.children[1].scope = node.scope
        check(node.children[1])
        node.elemNum = node.children[1].elemNum
        # node.type = node.children[1].type
        node.code = node.children[1].code

def calculate_lista_izraza_pridruzivanja(node):
    productionText = getProductionText(node)
    if productionText == '<izraz_pridruzivanja>':
        node.children[0].type = node.type
        calculate_izraz_pridruzivanja(node.children[0])
        node.elemNum = 1
        node.value = [node.children[0].value]
    elif productionText == '<lista_izraza_pridruzivanja> ZAREZ <izraz_pridruzivanja>':
        node.children[0].type = node.type
        calculate_lista_izraza_pridruzivanja(node.children[0])
        node.children[2].type = node.type
        calculate_izraz_pridruzivanja(node.children[2])
        node.elemNum = node.children[0].elemNum + 1
        node.value = node.children[0].value + [node.children[2].value]

def lista_izraza_pridruzivanja(node):
    productionText = getProductionText(node)
    if productionText == '<izraz_pridruzivanja>':
        node.children[0].scope = node.scope
        check(node.children[0])
        # node.type = [node.children[0].type]
        node.elemNum = 1
        node.code = node.children[0].code + '\n'
        if node.children[0].inc:
            node.code += ' PUSH R0\n'
        node.inc = node.children[0].inc
    elif productionText == '<lista_izraza_pridruzivanja> ZAREZ <izraz_pridruzivanja>':
        node.children[0].scope = node.scope
        check(node.children[0])
        node.children[2].scope = node.scope
        check(node.children[2])
        # node.type = node.children[0] + [node.children[2].type]
        node.elemNum = node.children[0].elemNum + 1
        node.code = node.children[0].code + '\n' + node.children[2].code + '\n'
    
def check(node : Node):
    if node.content == '<primarni_izraz>':
        primarni_izraz(node)
    elif node.content == '<postfiks_izraz>':
        postfiks_izraz(node)
    elif node.content == '<lista_argumenata>':
        lista_argumenata(node)
    elif node.content == '<unarni_izraz>':
        unarni_izraz(node)
    elif node.content == '<unarni_operator>':
        pass
    elif node.content == '<cast_izraz>':
        cast_izraz(node)
    elif node.content == '<ime_tipa>':
        ime_tipa(node)
    elif node.content == '<specifikator_tipa>':
        specifikator_tipa(node)
    elif node.content == '<multiplikativni_izraz>':
        multiplikativni_izraz(node)
    elif node.content == '<aditivni_izraz>':
        aditivni_izraz(node)
    elif node.content == '<odnosni_izraz>':
        odnosni_izraz(node)
    elif node.content == '<jednakosni_izraz>':
        jednakosni_izraz(node)
    elif node.content == '<bin_i_izraz>':
        bin_i_izraz(node)
    elif node.content == '<bin_xili_izraz>':
        bin_xili_izraz(node)
    elif node.content == '<bin_ili_izraz>':
        bin_ili_izraz(node)
    elif node.content == '<log_i_izraz>':
        log_i_izraz(node)
    elif node.content == '<log_ili_izraz>':
        log_ili_izraz(node)
    elif node.content == '<izraz_pridruzivanja>':
        izraz_pridruzivanja(node)
    elif node.content == '<izraz>':
        izraz(node)
    elif node.content == '<slozena_naredba>':
        slozena_naredba(node)
    elif node.content == '<lista_naredbi>':
        lista_naredbi(node)
    elif node.content == '<naredba>':
        naredba(node)
    elif node.content == '<izraz_naredba>':
        izraz_naredba(node)
    elif node.content == '<naredba_grananja>':
        naredba_grananja(node)
    elif node.content == '<naredba_petlje>':
        naredba_petlje(node)
    elif node.content == '<naredba_skoka>':
        naredba_skoka(node)
    elif node.content == '<prijevodna_jedinica>':
        prijevodna_jedinica(node)
    elif node.content == '<vanjska_deklaracija>':
        vanjska_deklaracija(node)
    elif node.content == '<definicija_funkcije>':
        definicija_funkcije(node)
    elif node.content == '<lista_parametara>':
        lista_parametara(node)
    elif node.content == '<deklaracija_parametra>':
        deklaracija_parametra(node)
    elif node.content == '<lista_deklaracija>':
        lista_deklaracija(node)
    elif node.content == '<deklaracija>':
        deklaracija(node)
    elif node.content == '<lista_init_deklaratora>':
        lista_init_deklaratora(node)
    elif node.content == '<init_deklarator>':
        init_deklarator(node)
    elif node.content == '<izravni_deklarator>':
        izravni_deklarator(node)
    elif node.content == '<inicijalizator>':
        inicijalizator(node)
    elif node.content == '<lista_izraza_pridruzivanja>':
        lista_izraza_pridruzivanja(node)

# def checkDefined(node):
#     if node.characterTable != None:
#         for key, value in node.characterTable.items():
#             if isFunction(value['type']) and not isDefined(key):
#                 raise Exception('funkcija')
#     for child in node.children:
#         checkDefined(child)

# try:
#     check(rootNode)
#     if not isDefined('main') or rootNode.characterTable['main']['type'] != 'funkcija(void → int)':
#         raise Exception('main')
    
# except Exception as exception:
#     # traceback.print_tb(exception.__traceback__)
#     print(exception)

check(rootNode)

rootNode.code = \
    ''' MOVE 40000, R7
 MOVE R7, R6
 CALL f_main
 HALT

''' +\
    rootNode.code +\
    globalCode

with open('a.frisc','w') as f:
    f.write(rootNode.code)

def printCode(node, i=0):
    print(' '*i, node.content, end='')
    if node.code != None:
        print(node.code)
    for child in node.children:
        printCode(child, i+1)

# printCode(rootNode)