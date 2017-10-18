# -*- coding: utf-8 -*-
from __future__ import unicode_literals


import operator
try:
    import ujson
except:
    import json as ujson

from kopy.funcs.utils import getfilePath, joinK, splitK, jaum_list


class KoPy_func():

    def __init__(self):
        self.bigram = ujson.load(open(getfilePath('database/bigram.json'),'r'))
        self.database = ujson.load(open(getfilePath('database/posList.json'),'r'))
        self.posbigram = ujson.load(open(getfilePath('database/posBigram.json'),'r'))
        self.verb = ujson.load(open(getfilePath('database/verbchange.json'), 'r'))

    def has_word(self, word):
        try:
            self.database[word]
        except:
            return False

        return True

    def getData(self, word, all=None):
        if not self.has_word(word):
            return False
        data = self.database[word]
        if all == None:
            result = [[(joinK(word),str(a)),b] for a, b in data.items()]
            result = sorted(result, key=operator.itemgetter(1),reverse=True)[0]
            return result[0]
        else:
            return data


    def getback(self, word1, word2=None, tag1=None, f=None, v=None):
        try:
            self.bigram[word1]
        except:
            return False
        if word2 == None:
            return self.bigram[word1]
        elif tag1 == None:
            cands = [b for b in self.bigram[word1].keys()]
        else:
            cands = [tag1]
        possible = []
        for i in range(len(cands)):
            try:
                possible.append(sorted([[(word2, key), value, cands[i]] for key, value in
                                        self.bigram[word1][cands[i]][word2].items()], key=operator.itemgetter(1),
                                       reverse=True)[0])
            except:
                continue
        possible = sorted(possible, key=operator.itemgetter(1), reverse=True)
        if possible == []:
            return False
        else:
            if f != None:
                return possible[0][2]
            if v != None:
                return possible[0][1]
        return possible[0][0]

    def getMid(self,forward,mid,back):
        cands = self.bigram[forward[0]][forward[1]][mid].keys()
        keys = list()
        for key in cands:
            try:
                self.bigram[mid][key][back]
                keys.append(key)
            except:
                continue
        if len(keys) == 1:
            return (mid,keys[0])
        elif keys == []:
            return False
        else:
            container = []
            for key in keys:
                rate = self.bigram[forward[0]][forward[1]][mid][key] * self.posbigram[key][self.getback(mid,back,key)[1]]
                container.append((key,rate))
            return (mid,sorted(container, key=operator.itemgetter(1), reverse=True)[0][0])




    #########################################################

    def pos(self, sentences):
        phrases = splitK(sentences.strip()).split()
        cont = []
        for phrase in phrases:
            p = phrase
            phrase = self.checkVerb(phrase)
            patterns = list()
            for i in phrase:
                patterns.extend(self.makePatterns(i))
            patterns = self.checkPossible(patterns)
            print(patterns)
            comp = list()
            extra = list()
            if cont == []:
                for pattern in patterns:
                    results,right = self.putTags(pattern)
                    if results != False and results != [False]:
                        if right:
                            comp.append(results)
                        else:
                            extra.append(results)
            else:
                for pattern in patterns:
                    results,right = self.putTags(pattern,cont[-1])
                    if results != False and results != [False]:
                        if right:
                            comp.append(results)
                        else:
                            extra.append(results)
            patterns = [i for i in comp if i]
            extra = [i for i in extra if i]
            patterns = sorted([(pattern,self.getRate(pattern)) for pattern in patterns],key=operator.itemgetter(1),reverse=True)
            extra = sorted([(pattern, self.getRate(pattern)) for pattern in extra],key=operator.itemgetter(1), reverse=True)
            go = True
            if patterns != []:
                for pattern in patterns:
                    if not False in pattern[0]:
                        if pattern[1] != 0:
                            cont.extend(pattern[0])
                            go = False
                            break
            if go and extra != []:
                for pattern in extra:
                    if not False in pattern[0]:
                        if pattern[1] != 0:
                            cont.extend(pattern[0])
                            go = False
                            break
            if go:
                for i in range(len(p)):
                    try:
                        if 'J' in self.getData(p[i:])[1]:
                            cont.extend([(joinK(p[:i]),'UN'),self.getData(p[i:])])
                            break
                    except:continue
                else:
                    cont.append((joinK(p),'UN'))

        if cont != []:
            return cont
        else:
            return ''

    def checkVerb(self,phrase):
        possible = list()
        s = [i for i in self.verb['ugan'].keys() if i+"ㅇ" in phrase]
        b = [i for i in self.verb['ㅂ'] if i + "ㅇ" in phrase]
        h = [i for i in self.verb['ㅎ'].keys() if i in phrase]
        ya = [i for i in self.verb['ㅘ'].keys() if i in phrase]
        eu = [i for i in self.verb['르'] if i in phrase]

        # 최장 어미 분별 & ㄹ 불규칙 변화
        c = []
        for i in self.verb['ㄹ']:
            if i in phrase:
                if c == []:c.append(i)
                elif len(c[0])<len(i):
                    c.pop();c.append(i)
        try:
            l = c.pop()
            index = phrase.find(l)
            for q in range(index):
                if self.has_word(phrase[q:index]+'ㄹ'):
                    p = [i for i in self.getData(phrase[q:index]+'ㄹ', True).keys() if 'V' in i]
                    if p != []:
                        possible.append(phrase.replace(l,'ㄹ'+l,1))
                        break
        except:
            pass

        possible.append(phrase)

        if 'ㅝ' in phrase:
            phrase = phrase.replace('ㅝ','ㅜㅇㅓ')
            possible.append(phrase)
        if 'ㅕ' in phrase:
            phrase = phrase.replace('ㅕ','ㅣㅇㅓ')
            possible.append(phrase)
        if 'ㅇㅗㄴㅓㄹㅏ' in phrase:
            phrase = phrase.replace('ㅇㅗㄴㅓㄹㅏ','ㅇㅗㅇㅓㄹㅏ')
            possible.append(phrase)
        if 'ㄷㅏㅇㅗ' in phrase:
            phrase = phrase.replace('ㄷㅏㅇㅗ','ㅈㅜㅇㅗ')
            possible.append(phrase)
        if 'ㄷㅏㄹㄹㅏ' in phrase:
            phrase = phrase.replace('ㄷㅏㄹㄹㅏ','ㅈㅜㄹㅏ')
            possible.append(phrase)


        for ph in range(len(possible)):
            for i in s:
                possible.append(possible[ph].replace(i,self.verb['ugan'][i]))

        for pa in range(len(possible)):
            for i in b:
                ph = possible[pa]
                index = ph.find(i) + len(i)
                if ph[index:index+2] == 'ㅇㅜ':
                    possible.append(ph[:index]+'ㅂㅇㅡ'+ph[index+2:])
                    possible.append(ph[:index] + 'ㅂ' + ph[index + 2:])
                elif ph[index:index + 2] == 'ㅇㅝ':
                    possible.append(ph[:index]+'ㅂㅇㅓ'+ph[index+2:])
                elif ph[index:index + 2] == 'ㅇㅘ':
                    possible.append(ph[:index] + 'ㅂㅇㅏ' + ph[index + 2:])


        for ph in range(len(possible)):
            for i in eu:
                possible.append(possible[ph].replace(i,self.verb['르'][i]))

        for ph in range(len(possible)):
            if 'ㅎㅐ' in possible[ph]:
                possible.append(possible[ph].replace('ㅎㅐ','ㅎㅏㅇㅕ'))
                possible.append(possible[ph].replace('ㅎㅐ', 'ㅎㅏㅇㅓ'))

        for ph in range(len(possible)):
            for i in h:
                possible.append(possible[ph].replace(i, self.verb['ㅎ'][i]))

        for ph in range(len(possible)):
            for i in ya:
                possible.append(possible[ph].replace(i,self.verb['ㅘ'][i]))

        return possible


    def makePatterns(self, phrase):
        memory = []

        for i in range(len(phrase)):
            if memory == []:
                if self.has_word(phrase[:i+1]):
                    memory.append([phrase[:i+1]])
                else:continue
            else:
                memory.append([])
                for n in memory[:-1]:
                    for c in n:
                        index = sum([len(d) for d in c.split('+')])
                        if self.has_word(phrase[index:i+1]):
                            memory[-1].extend([c + "+" + phrase[index:i +1]])
                        else:continue
                if self.has_word(phrase[0:i+1]):
                    memory[-1].append(phrase[0:i+1])
                if memory[-1] == []:
                    memory.pop()
        result = []
        for i in memory[-1]:
            if phrase == ''.join(i.split('+')):
                result.append(i)
        return result

    def checkPossible(self,memory):
        bigram = list()

        for index in range(len(memory)):
            pos = memory[index]
            possible = True
            splited = [joinK(b) for b in pos.split('+')]
            for i in range(1,len(splited)):
                if not self.getback(splited[i-1],splited[i]):
                    possible = False
                    if 'V' in ''.join(self.getData(splitK(splited[i-1]),True).keys()):
                        if 'E' in ''.join(self.getData(splitK(splited[i]),True).keys()):
                            if splitK(splited[i-1])[-1] in jaum_list:
                                jung = splitK(splited[i-1])[-2]
                            else:jung = splitK(splited[i-1])[-1]
                            if jung in ['ㅓ','ㅜ','ㅡ','ㅣ']:
                                jung = 'ㅇㅓ'
                            elif jung in ['ㅏ','ㅗ']:
                                jung = 'ㅇㅏ'
                            print(jung)
                            if self.getback(splited[i-1],joinK(jung)+splited[i]):
                                print('okay')
                                pos = pos.replace(splitK(splited[i]),jung+splitK(splited[i]),1)
                                print(pos)
                                possible = True
            if possible == True:
                bigram.append(pos)
        if bigram == []:
            return memory
        return bigram


    def putTags(self,pattern,forward=None):
        container = list()
        splited_pattern = pattern.split('+')
        right = True
        for counter, word in enumerate(splited_pattern):
            if counter == 0:
                if forward:
                    try:
                        tag = self.getMid(forward, joinK(word),joinK(splited_pattern[counter+1]))
                        if tag != False:
                            container.append(tag)
                        else:
                            right = False
                            try:
                                container.append(self.getFirstPos(word, splited_pattern[counter + 1]))
                            except:
                                container.append(self.getData(word))
                    except:
                        right = False
                        try:
                            container.append(self.getFirstPos(word, splited_pattern[counter + 1]))
                        except:
                            container.append(self.getData(word))
                else:
                    try:
                        container.append(self.getFirstPos(word,splited_pattern[counter+1]))
                    except:
                        right = False
                        container.append(self.getData(word))
            elif counter == len(splited_pattern)-1:
                try:
                    tag = self.getback(container[counter-1][0],joinK(word),container[counter-1][1])
                    if tag != False:
                        container.append(tag)
                    else:
                        right = False
                        tag = self.getback(container[-1][0],joinK(word))
                        if tag != False:
                            container.append(tag)
                        else:
                            container.append(self.getData(word))
                except:
                    container = False
                    break
            else:
                if 'V' in container[-1][1]:
                    if word in jaum_list:
                        f = splitK(container[-1][0])
                        if f[-1] in jaum_list:
                            m = f[-2]
                        else:m = f[-1]
                        if m in ['ㅕ','ㅓ','ㅜ','ㅡ','ㅣ','ㅐ']:
                            word = "ㅇㅓ"+word
                        elif m in ['ㅏ','ㅗ']:
                            word = 'ㅇㅏ'+word
                try:
                    tag = self.getMid(container[-1],joinK(word),joinK(splited_pattern[counter+1]))
                    if tag != False:
                        container.append(tag)
                    else:
                        right = False
                        tag = self.getback(container[-1][0], joinK(word))
                        if tag != False:
                            container.append(tag)
                        else:
                            container.append(self.getData(word))
                except:
                    right = False
                    tag = self.getback(container[-1][0], joinK(word))
                    if tag != False:
                        container.append(tag)
                    else:
                        if self.getData(word) != False:
                            container.append(self.getData(word))
                        else:
                            container = False
                            break

        if len(splited_pattern) == 1:
            right = True
        return container,right


    def getFirstPos(self,word1,word2):
        word1 = joinK(word1)
        word2 = joinK(word2)
        cands = [b for b in self.bigram[word1].keys()]
        possible = []
        for i in range(len(cands)):
            try:
                self.bigram[word1][cands[i]][word2]
                possible.append(cands[i])
            except:
                continue
        if len(possible)>1:
            data = self.getData(splitK(word1),all=True)
            possible = sorted([(pos,data[pos]) for pos in possible],key=operator.itemgetter(1),reverse=True)[0]
        return (word1,possible[0])

    def getRate(self,pattern):
        rate = 1
        for count,pos in enumerate(pattern):
            try:
                if count == 0:
                    rate = (float(self.getData(splitK(pos[0]),all=True)[pos[1]]) * float(self.posbigram['^start'][pos[1]]))/100
                else:
                    rate = rate * (float(self.getData(splitK(pos[0]),all=True)[pos[1]]) * float(self.posbigram[pattern[count-1][1]][pos[1]]))/100
            except:
                rate = 0
        return rate * 100


if __name__ == "__main__":
    pass
