import sys

def lerArquivo():
    arquivo = input('Digite o nome do arquivo: ')
    if arquivo.find('.txt') == -1:
        sys.exit()

    restricao = []
    with open(arquivo, 'r') as arquivo:
        objetivo = arquivo.readline()
        for linha in arquivo.readlines():
            if linha != '\n':
                restricao.append(linha.split(' '))
    return objetivo, restricao

def toFormaPadrao(objetivo, restricao):
    numVariaveis = len(restricao[-1]) - 2
    
    # adiciona variavel de folga ou de excesso
    padrao = []
    for r in restricao[:-1]:
        linha = []
        for e in r:
            if e == '<=':
                numVariaveis += 1
                linha.append('+')
                linha.append('x'+ str(numVariaveis))
                linha.append('=')
            elif e == '>=':
                numVariaveis += 1
                linha.append('-')
                linha.append('x'+ str(numVariaveis))
                linha.append('=')
            else:
                linha.append(e)
        padrao.append(linha)
    
    # checa valores das restrições
    for val in padrao:
        for e in range(len(val)-1):
            if val[e] == '=' and val[e+1] == '-':
                if val[0]=='-':
                    del(val[0])
                else:
                    val.insert(0, '-')
                el = 1
                while el < len(val):
                    if val[el]=='-':
                        val[el]='+'
                    elif val[el]=='+':
                        val[el]='-'
                    el+=1
        if val[-2] == '+': del(val[-2])

    linha = []
    for v in listaVariaveis(padrao)[:-1]:
        linha.append(v)
        linha.append(',')
    linha.append(listaVariaveis(padrao)[-1])
    linha.append('>=')
    linha.append('0')
    padrao.append(linha)

    return padrao

def listaVariaveis(restricao):
    var = []
    for r in restricao:
        for n in r:
            if 'x' in n and 'x'+n.split('x')[1] not in var:
                var.append('x'+n.split('x')[1])
    return var

def geraMatrizInicial(objetivo, padrao):
    # trata texto de entrada
    virgulas = padrao[-1].count(',')
    for _ in range(virgulas):
        padrao[-1].remove(',')
    for linha in padrao:
        vazio = linha.count('')
        for _ in range(vazio):
            linha.remove('')
    padrao[-1].remove('>=')
    padrao[-1].remove('0')
    
    # inicializa matriz  
    matriz = []
    for i in range(len(padrao)):
        aux = []
        for j in range(len(padrao[-1]) + 1):
            aux.append(0)
        matriz.append(aux)
    
    # preenche matriz criada
    padrao = padrao[:-1]
    linhas = 0
    for linha in padrao:
        i = 0
        while i < len(linha):
            if linha[i] == '-' or (i == 0 and linha[i][0] == '-'):
                if linha[i] == '-':
                    i += 1
                else:
                    linha[i] = linha[i][1:]

                val = linha[i].split('x')
                if val[0] != '':
                    matriz[linhas][int(val[1]) - 1] = -int(val[0])
                else:
                    matriz[linhas][int(val[1]) - 1] = -1
            elif linha[i] == '+' or (i == 0 and linha[i][0] != '-'):
                if linha[i] == '+':
                    i += 1
                val = linha[i].split('x')
                if val[0] != '':
                    matriz[linhas][int(val[1]) - 1] = int(val[0])
                else:
                    matriz[linhas][int(val[1]) - 1] = 1
            else:
                i += 1
                matriz[linhas][-1] = int(linha[i][ :len(linha[i]) - 1]) 
            i += 1
        linhas += 1

    # preenche ultima linha da matriz
    objetivo = objetivo.split(' = ')
    tipo = objetivo[0].split(' ')[0]
    var = objetivo[1].split(' ')
    i = 0
    while i < len(var):
        if var[i] == '-':
            i += 1
            val = var[i].split('x')
            if val[0] != '':
                matriz[linhas][int(val[1]) - 1] = -int(val[0])
            else:
                matriz[linhas][int(val[1]) - 1] = -1
        elif var[i] == '+' or i == 0:
            if var[i] == '+':
                i += 1
            val = var[i].split('x')
            if val[0] != '':
                matriz[linhas][int(val[1]) - 1] = int(val[0])
            else:
                matriz[linhas][int(val[1]) - 1] = 1
        else:
            matriz[linhas][len(matriz[0]) - 1] = int(linha[i][ :len(linha[i]) - 1]) 
        i += 1
    matriz[-1][-1] = tipo
    return matriz

def lerMatriz(tableau):
    for l in range(len(tableau)):
        for n in range(len(tableau[0])):
            if l==len(tableau)-1 and n==len(tableau[-1])-1:
                if 'max' in tableau[-1][-1]:
                    tipo = 'max'
                    try: tableau[-1][-1] = float(tableau[-1][-1].replace('max', ''))
                    except:tableau[-1][-1] = 0.0
                else:
                    tipo = 'min'
                    try: tableau[-1][-1] = float(tableau[-1][-1].replace('min', ''))
                    except: tableau[-1][-1] = 0.0
            else: tableau[l][n]=float(tableau[l][n])
    return tableau, tipo

def simplex(tableau, tipo):
    base = acharBases(tableau)
    if (not len(base)==len(tableau)-1):
        print('O problema não possui base inicial.')
        return
    for l in tableau: 
        for n in range(len(l[:-1])):
            if l[-1] < 0:
                print('O problema não está na forma padrão.')
                return
    print('\nBase inicial: ', end='')
    print(base)
    printTableau(tableau, tipo, base)
    print('\nTransformação para forma canônica:')
    formaCanonica(tableau, base)
    printTableau(tableau, tipo, base)
    while True:
        baseEntra = novaBase(tableau, tipo)
        if baseEntra == None:
            print('Solução ótima: Z = ' + str(tableau[-1][-1] * -1))
            return
        baseSai = testeDaRazao(tableau, baseEntra)
        if baseSai == None:
            print('Problema de solução Ilimitada')
            return
        print('Sai '+str(base[baseSai])+', entra x'+ str(baseEntra+1))
        escalonar(tableau, baseEntra, baseSai)
        base[baseSai]='x'+str(baseEntra+1)
        printTableau(tableau, tipo, base)

def acharBases(tableau):
    bases = []
    for c in range(len(tableau[0])-1):
        aux = 0
        aux2 = 0
        for l in range(len(tableau)-1):
            if not tableau[l][c]==0 and not tableau[l][c]==1:
                aux=-1
            elif tableau[l][c]==1 and not aux==-1:
                aux+=1
                aux2=c
        if aux==1:
            bases.append('x'+str(aux2+1))
    base=[]
    for l in range(len(tableau)-1):
        for n in range(len(tableau[0])):
            for b in range(len(bases)):
                if tableau[l][n]==1 and ('x'+str(n+1) in bases[b]):
                    base.append(bases[b])
    return base

#imprime a tabela (precisão de 2 casas)
def printTableau(tableau, tipo, bases):
    maiores = [0]*len(tableau[0])
    for c in range(len(tableau[0])):
        maior = 2
        for l in range(len(tableau)):
            if len('{:.2f}'.format(tableau[l][c]))>maior: maior = len('{:.2f}'.format(tableau[l][c]))
            maiores[c]=maior
    print('      |', end = '')
    for c in range(len(tableau[0])):
        if c==len(tableau[0])-1:print(''+(' '*maiores[c])+'b', end='')
        else:print(''+(' '*maiores[c])+'x'+str(c+1)+' |', end='')
    print('\n-', end='')
    for c in range(len(tableau[0])):
        print('-'*(5+maiores[c]), end='')
    print()
    for l in range(len(tableau)):
        if l<len(tableau)-1: print(' '*(4-len(bases[l])) + bases[l] , end='')
        else: print('    ', end='')
        for n in range(len(tableau[0])):
            aux = len('{:.2f}'.format(tableau[l][n]))
            print('  | ', end ='')
            if l == len(tableau)-1 and n == len(tableau[0])-1 and tableau[-1][-1]==0: print(('  '*(maiores[n]-aux))+'Z', end='')
            elif l == len(tableau)-1 and n == len(tableau[0])-1 and tableau[-1][-1]>0: print(('  '*(maiores[n]-aux))+'Z+'+str(tableau[-1][-1]), end='')
            elif l == len(tableau)-1 and n == len(tableau[0])-1: print((' '*(maiores[n]-aux))+' Z'+'{:.2f}'.format(tableau[-1][-1]), end='')
            else: print((' '*(maiores[n]-aux))+'{:.2f}'.format(tableau[l][n]), end='')
        print()
    print()

def formaCanonica(tableau, bases):
    for b in range(len(bases)):
        coluna = int(bases[b][1:])-1
        if not tableau[-1][coluna] == 0:
            aux = tableau[-1][coluna]*-1
            for n in range(len(tableau[0])):
                tableau[-1][n]=tableau[-1][n]+tableau[b][n]*aux

#retorna o indice da coluna para a nova base
#returna None caso esteja na melhor solução
#deve estar na forma canonica
def novaBase(tableau, tipo):
    aux = 0
    aux2 = 0
    if tipo=='max':
        for n in range(len(tableau[-1])):
            if tableau[-1][n]>aux:
                aux=tableau[-1][n]
                aux2=n
        if aux==0: return None
        return aux2
    for n in range(len(tableau[-1])-1):
        if tableau[-1][n]<aux:
            aux=tableau[-1][n]
            aux2=n
    if aux==0: return None
    return aux2

def testeDaRazao(tableau, saindo):
    menor = []
    coluna = []
    for n in range(len(tableau)-1):
        if tableau[n][saindo] > 0:
            menor.append(tableau[n][-1]/tableau[n][saindo])
            coluna.append(n)
    if len(coluna)==0: return None
    return coluna[menor.index(min(menor, key=float))]
    
def escalonar(tableau, entra, sai):
    if not tableau[sai][entra]==1:
        aux = (tableau[sai][entra])
        for n in range(len(tableau[0])):
            tableau[sai][n]=tableau[sai][n]/aux
    for l in range(len(tableau)):
        if not l == sai:
            aux = tableau[l][entra]*-1
            for n in range(len(tableau[0])):
                tableau[l][n]=tableau[l][n]+(tableau[sai][n]*aux)

objetivo, restricao = lerArquivo() # Ler entrada
padrao = toFormaPadrao(objetivo, restricao) # Transforma a entrada para a forma padrão
tableau = geraMatrizInicial(objetivo, padrao) # Gera Matriz do tableau inicial
tableau, tipo = lerMatriz(tableau) # Ler matriz gerada
simplex(tableau, tipo) # Realiza o Simplex