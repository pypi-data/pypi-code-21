"""
PwStrength - Password Strength Test
Copyright (C) 2016 Dylan F. Marquis

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

__author__      = "Darksair"
__author__      = "Dylan F. Marquis"

import re
import math
import enchant

def findSeqChar(CharLocs, src):
    """Find all sequential chars in string `src'.  Only chars in
    `CharLocs' are considered. `CharLocs' is a list of numbers.  For
    example if `CharLocs' is [0,2,3], then only src[2:3] is a possible
    substring with sequential chars.
    """
    AllSeqChars = []
    i = 0
    SeqChars = []
    while i < len(CharLocs) - 1:
        if CharLocs[i + 1] - CharLocs[i] == 1 and \
               ord(src[CharLocs[i+1]]) - ord(src[CharLocs[i]]) == 1:
            # We find a pair of sequential chars!
            if not SeqChars:
                SeqChars = [src[CharLocs[i]], src[CharLocs[i+1]]]
            else:
                SeqChars.append(src[CharLocs[i+1]])
        else:
            if SeqChars:
                AllSeqChars.append(SeqChars)
                SeqChars = []

        i += 1
    if SeqChars:
        AllSeqChars.append(SeqChars)

    return AllSeqChars

def findDictWord(pw):

    CharSubstring = []
    EngDict = enchant.Dict("en_US")
    AlphaStr = ''

    CharSubstring =  re.split(r'[0123456789`\-=~!@#$%^&*()_+\[\]{};\'\\:"|<,./<>?]', pw)
    for SubStr in CharSubstring:
        AlphaStr += SubStr
        if len(SubStr) >= 3:
            if EngDict.check(SubStr):
                return True

    Position = 0
    Iter = 0
    for Letter in AlphaStr:
        while Iter <= len(AlphaStr):
                try:
                    if (EngDict.check(AlphaStr[Position:(Iter-len(AlphaStr))])) and\
                       (len(AlphaStr[Position:(Iter-len(AlphaStr))]) >= 3):
                        return True
                except:
                    pass
                Iter += 1
        Iter = 0
        Position += 1
    return False

def extraCriteria(pw):
    mask = 0x00

    if len(pw) >= 8:
        mask = mask | 0x001

    if re.compile('[a-z]+').findall(pw):
        mask = mask | 0x002


    if re.compile('[A-Z]+').findall(pw):
        mask = mask | 0x004

    if re.compile('[0-9]+').findall(pw):
        if re.compile('[0-9]{2,}').findall( pw):
            mask = mask | 0x012
        else:
            mask = mask | 0x08

    if re.compile('[`\-=~!@#$%^&*()_+\[\]{};\'\\:"|<,./<>?]').findall(pw):
        mask = mask | 0x026


    #Score of 0 if length is under 8 chars
    if (mask%2) == 0:
        return 0

    elif mask == 15:
        return 6

    elif mask == 23:
        return 8

    elif mask == 39:
        return 6

    elif mask == 55:
        return 10

    elif mask == 47:
        return 8

    else:
        return 0


def pwStrength(pw):
    Score = 0
    Length = len(pw)
    Score += Length * 4

    NUpper = 0
    NLower = 0
    NNum = 0
    NSymbol = 0
    LocUpper = []
    LocLower = []
    LocNum = []
    LocSymbol = []
    CharDict = {}


    for i in range(Length):
        Ch = pw[i]
        Code = ord(Ch)

        if Code >= 48 and Code <= 57:
            NNum += 1
            LocNum.append(i)
        elif Code >= 65 and Code <= 90:
            NUpper += 1
            LocUpper.append(i)
        elif Code >= 97 and Code <= 122:
            NLower += 1
            LocLower.append(i)
        else:
            NSymbol += 1
            LocSymbol.append(i)

        if not Ch in CharDict:
            CharDict[Ch] = 1
        else:
            CharDict[Ch] += 1

    if NUpper != Length and NLower != Length:
        if NUpper != 0:
            Score += (Length - NUpper) * 2
            # print("Upper case score:", (Length - NUpper) * 2)
        if NLower != 0:
            Score += (Length - NLower) * 2
            # print("Lower case score:", (Length - NLower) * 2)

    if NNum != Length:
        Score += NNum * 4
        # print("Number score:", NNum * 4)
    Score += NSymbol * 6
    # print("Symbol score:", NSymbol * 6)

    # Middle number or symbol
    Score += len([i for i in LocNum if i != 0 and i != Length - 1]) * 2
    # print("Middle number score:", len([i for i in LocNum if i != 0 and i != Length - 1]) * 2)
    Score += len([i for i in LocSymbol if i != 0 and i != Length - 1]) * 2
    # print("Middle symbol score:", len([i for i in LocSymbol if i != 0 and i != Length - 1]) * 2)

    # Letters only?
    if NUpper + NLower == Length:
        Score -= Length
        # print("Letter only:", -Length)
    if NNum == Length:
        Score -= Length
        # print("Number only:", -Length)

    # Repeating chars
    Repeats = 0
    for Ch in CharDict:
        if CharDict[Ch] > 1:
            Repeats += CharDict[Ch] - 1
    if Repeats > 0:
        Score -= int(Repeats / (Length - Repeats)) + 1
        # print("Repeating chars:", -int(Repeats / (Length - Repeats)) - 1)

    if Length > 2:
        # Consequtive letters
        for MultiLowers in re.findall(''.join(["[a-z]{2,", str(Length), '}']), pw):
            Score -= (len(MultiLowers) - 1) * 2
            # print("Consequtive lowers:", -(len(MultiLowers) - 1) * 2)
        for MultiUppers in re.findall(''.join(["[A-Z]{2,", str(Length), '}']), pw):
            Score -= (len(MultiUppers) - 1) * 2
            # print("Consequtive uppers:", -(len(MultiUppers) - 1) * 2)

        # Consequtive numbers
        for MultiNums in re.findall(''.join(["[0-9]{2,", str(Length), '}']), pw):
            Score -= (len(MultiNums) - 1) * 2
            # print("Consequtive numbers:", -(len(MultiNums) - 1) * 2)

        # Sequential letters
        LocLetters = (LocUpper + LocLower)
        LocLetters.sort()
        for Seq in findSeqChar(LocLetters, pw.lower()):
            if len(Seq) > 2:
                Score -= (len(Seq) - 2) * 2
                # print("Sequential letters:", -(len(Seq) - 2) * 2)

        # Sequential numbers
        for Seq in findSeqChar(LocNum, pw.lower()):
            if len(Seq) > 2:
                Score -= (len(Seq) - 2) * 2
                # print("Sequential numbers:", -(len(Seq) - 2) * 2)


    if findDictWord(pw) is True:
        Score -= 20

    Score += extraCriteria(pw)

    return Score

def prettyScore(pw):
    Score = pwStrength(pw)

    if Score < 0:
        return "Very Weak"

    elif 0 < Score <= 64:
        return "Weak"

    elif 64 < Score <= 74:
        return "Fair"

    elif 74 < Score <= 89:
        return "Strong"

    elif Score >= 90:
        return "Very Strong"

def passwordEntropy(pw):
    """
    Based on NIST SP 800-63 - Claude Shannon Method
    This does not follow Wolfram's entropy calculation
    """
    i = 0
    entropy = 0.0
    for letter in pw:
        i+=1
        if i == 1:
            entropy += 4.0
        if 1 < i < 9:
            entropy += 2.0
        if 8 < i < 21:
            entropy += 1.5
        if i > 20:
            entropy += 1

    if re.compile("[A-Z0-9]").findall(pw) or\
       re.compile('[A-Z`\-=~!@#$%^&*()_+\[\]{};\'\\:"|<,./<>?]').findall(pw):
        entropy += 6

    if findDictWord(pw) is False and len(pw) < 21:
        entropy += 6

    return entropy

def prettyPasswordEnumeration(num,rate):
    """
    Accepts number of passwords and the rate (i.e. 100,000 password guesses per second
    """
    sec = num/rate
    if sec < 61:
        return "{0} seconds".format(sec)
    else:
        if sec/60 < 61:
            return "{0} minutes".format(round(sec/60,2))
        else:
            if (sec/60) < 25:
                return "{0} hours".format((sec/60)/60)
            else:
                if ((sec/60)/60)/24 < 366:
                    return "{0} days".format(((sec/60)/60)/24)
                else:
                    rem = (((sec/60)/60)/24)/365
                    if rem < 1000001:
                        return "{0} years".format(round(rem,2))
                    else:
                        rem = rem/1000000
                        if rem < 1001:
                            return "{0} million years".format(round(rem,2))
                        else:
                            return "{0} billion years".format(round(rem/1000,2))


def passwordNumber(pw):
    entropy = passwordEntropy(pw)
    numPasswd = math.pow(2, entropy)
    return numPasswd
