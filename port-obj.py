import sys
import re
havePyperclip = False
try:
    import pyperclip
except ImportError:
    print('Pyperclip not found. Copying to clipboard will not work.')
else:
    havePyperclip = True

'''
This is going unused for now. Folder creation through the console is iffy.

def makeFolderCmd(name: str, id: str) -> str:
    part1 = 'state = Calc.getState()\nstate.expressions.list.push({type: "folder", title: "'
    part2 = '", id: "'
    part3 = '"})\nCalc.setState(state)'
    return part1 + name + part2 + id + part3
'''

def makeExpressionCmd(latex: str, id: str) -> str:
    part1 = 'Calc.setExpressions([{type: "expression", latex: "'
    part2 = '", id: "'
    part3 = '"}])'
    return part1 + latex + part2 + id + part3

path = ''
option = 2 # default to sending to file

if (len(sys.argv) == 1):
    print('Usage: python port-obj.py [-cdf] [path to .obj file]')
    print('Options:')
    print('-c: print console commands to stdout')
    print('-d: copy equations directly to clipboard')
    print('-f: print console commands to a file')
    print('Use only one of these at once. The script is pretty brittle.')
    exit(1)
elif (len(sys.argv) == 2):
    path = str(sys.argv[1])
elif (len(sys.argv) == 3):
    if (str(sys.argv[1]) == '-c'):
        # console commands to stdout
        option = 0
    if (str(sys.argv[1]) == '-d'):
        # equations directly to clipboard
        option = 1
    if (str(sys.argv[1]) == '-f'):
        # console commands to a file
        option = 2
    path = str(sys.argv[2])
    

# vertex coordinates
vertices = [[], [], []]

# indices for the triangle face vertices
triangles = [[], [], []]
try:
    with open(path, 'r') as f:
        for line in f:
            if line.startswith('v '):
                # vertex
                # v x y z
                l = re.split(r'\s+', line)
                # to correct for how blender vs desmos handles the z axis
                vertices[0].append(l[1])
                vertices[1].append(l[3])
                vertices[2].append(l[2])
            elif line.startswith('f '):
                # face
                # for now only care about the face
                # worry about texture later
                l = re.split(r'\s+', line)
                
                # technically there can be more sides than 3 on a face
                # but for now we only care about triangles

                # naively take the first 3 vertices and ignore the rest
                t1 = int(l[1].split('/')[0])
                t2 = int(l[2].split('/')[0])
                t3 = int(l[3].split('/')[0])

                if t1 < 0:
                    t1 += len(vertices[0])
                if t2 < 0:
                    t2 += len(vertices[0])
                if t3 < 0:
                    t3 += len(vertices[0])
                
                triangles[0].append(t1)
                triangles[1].append(t2)
                triangles[2].append(t3)

except IOError:
    print('File not found: ' + path)

if option == 0 or option == 2:
    v1Exp = makeExpressionCmd('v_1=[' + ','.join(vertices[0]) + ']', 'v1')
    v2Exp = makeExpressionCmd('v_2=[' + ','.join(vertices[1]) + ']', 'v2')
    v3Exp = makeExpressionCmd('v_3=[' + ','.join(vertices[2]) + ']', 'v3')

    t1Exp = makeExpressionCmd('t_1=[' + ','.join(map(str, triangles[0])) + ']', 't1')
    t2Exp = makeExpressionCmd('t_2=[' + ','.join(map(str, triangles[1])) + ']', 't2')
    t3Exp = makeExpressionCmd('t_3=[' + ','.join(map(str, triangles[2])) + ']', 't3')

    consLatex = '\\\\left[\\\\operatorname{triangle}\\\\left(\\\\left(v_{1}\\\\left[t_{1}\\\\left[x\\\\right]\\\\right],v_{2}\\\\left[t_{1}\\\\left[x\\\\right]\\\\right],v_{3}\\\\left[t_{1}\\\\left[x\\\\right]\\\\right]\\\\right),\\\\left(v_{1}\\\\left[t_{2}\\\\left[x\\\\right]\\\\right],v_{2}\\\\left[t_{2}\\\\left[x\\\\right]\\\\right],v_{3}\\\\left[t_{2}\\\\left[x\\\\right]\\\\right]\\\\right),\\\\left(v_{1}\\\\left[t_{3}\\\\left[x\\\\right]\\\\right],v_{2}\\\\left[t_{3}\\\\left[x\\\\right]\\\\right],v_{3}\\\\left[t_{3}\\\\left[x\\\\right]\\\\right]\\\\right)\\\\right)\\\\operatorname{for}x=\\\\left[1,...,' + str(len(vertices[0])) + '\\\\right]\\\\right]'

    consExp = makeExpressionCmd(consLatex, 'cons')

    if option == 0:
        # print commands to stdout
        print(v1Exp, v2Exp, v3Exp, t1Exp, t2Exp, t3Exp, consExp, sep='\n')
    if option == 2:
        # send commands to a file
        if path.endswith('.obj'):
            path = path[:-4] + '.commands'
        else:
            path += '.commands'
        with open(path, 'w') as f:
            f.write(v1Exp + '\n' +
                    v2Exp + '\n' +
                    v3Exp + '\n' +
                    t1Exp + '\n' +
                    t2Exp + '\n' +
                    t3Exp + '\n' +
                    consExp + '\n')
        print('Copy the contents of ' + path + ' into the JS console on Desmos.')

if option == 1:

    # copy equations to clipboard
    v1Exp = 'v_1=[' + ','.join(vertices[0]) + ']'
    v2Exp = 'v_2=[' + ','.join(vertices[1]) + ']'
    v3Exp = 'v_3=[' + ','.join(vertices[2]) + ']'
    t1Exp = 't_1=[' + ','.join(map(str, triangles[0])) + ']'
    t2Exp = 't_2=[' + ','.join(map(str, triangles[1])) + ']'
    t3Exp = 't_3=[' + ','.join(map(str, triangles[2])) + ']'
    consLatex = '\\left[\\operatorname{triangle}\\left(\\left(v_{1}\\left[t_{1}\\left[x\\right]\\right],v_{2}\\left[t_{1}\\left[x\\right]\\right],v_{3}\\left[t_{1}\\left[x\\right]\\right]\\right),\\left(v_{1}\\left[t_{2}\\left[x\\right]\\right],v_{2}\\left[t_{2}\\left[x\\right]\\right],v_{3}\\left[t_{2}\\left[x\\right]\\right]\\right),\\left(v_{1}\\left[t_{3}\\left[x\\right]\\right],v_{2}\\left[t_{3}\\left[x\\right]\\right],v_{3}\\left[t_{3}\\left[x\\right]\\right]\\right)\\right)\\operatorname{for}x=\\left[1,...,' + str(len(vertices[0])) + '\\right]\\right]'
    combined = v1Exp + '\n' + v2Exp + '\n' + v3Exp + '\n' + t1Exp + '\n' + t2Exp + '\n' + t3Exp + '\n' + consLatex
    if havePyperclip:
        pyperclip.copy(combined)
        print('Equations copied to clipboard. Paste those into the Desmos expression list.')
    else:
        print('Pyperclip not found. Printing equations to stdout.')
        print('Equations:')
        print(combined)
        print('Copy those into the Desmos expression list.')
