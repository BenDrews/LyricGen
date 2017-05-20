import sys, getopt, nltk, re, string, random, codecs, glob, datamuse, pronouncing, rhyme
from nltk.tokenize import RegexpTokenizer
from nltk.util import bigrams, trigrams
from nltk.corpus import cmudict
from curses.ascii import isdigit

CMU_DICT = cmudict.dict()
ALPHA_EXP = re.compile("[A-Za-z]+")

class StressNode:
    def __init__(self):
        self.count = 0
        self.tokens = {}

    def observeWord(self, word):
        self.count += 1
        if not self.tokens.has_key(word):
            self.tokens[word] = 1
        else:
            self.tokens[word] += 1

    def getUChild(self):
        if not hasattr(self, 'uChild'):
            self.uChild = StressNode()
        return self.uChild

    def getSChild(self):
        if not hasattr(self, 'sChild'):
            self.sChild = StressNode()
        return self.sChild

    def getWord(self, index):
        for token in self.tokens:
            index -= self.tokens[token]
            if index < 0:
                return token
        print 'Cannot generate word'
        return ''

    def getTotal(self):
        result = self.count
        if hasattr(self, 'uChild'):
            result += self.uChild.getTotal()
        if hasattr(self, 'sChild'):
            result += self.sChild.getTotal()
        return result

    def strContent(self):
        result = str(self.tokens.keys())

        if hasattr(self, 'uChild'):
            result += '\n\nUnstressed Child\n\n' + self.uChild.strContent()
        if hasattr(self, 'sChild'):
            result += '\n\nStressed Child\n\n' + self.sChild.strContent()
        return result
    
class StressTree:
    def __init__(self, prefix):
        self.prefix = prefix
        self.root = StressNode()

    def observeWord(self, word):
        stress = getStress(word)
        if stress == '*':
            self.root.observeWord(word)
        else:
            current = self.root
            for syl in stress:
                if syl == '0':
                    current = current.getUChild()
                else:
                    current = current.getSChild()
            current.observeWord(word)

    def strContent(self):
        return self.root.strContent()

    def getCount(self, stress):
        if stress == '*':
            return self.root.count
        else:
            result = 0
            current = self.root
            for syl in stress:
                if syl == '0':
                    current = current.getUChild()
                else:
                    current = current.getSChild()
                result += current.count
                
            return result

    def getTotal(self):
        result = 0
        if hasattr(self.root, 'uChild'):
            result += self.root.uChild.getTotal()
        if hasattr(self.root, 'sChild'):
            result += self.root.sChild.getTotal()
        return result

    def generateFreeWord(self):
        count = self.getTotal()
        if count == 0:
            if self.root.count == 0:
                print 'Cannot generate word'
                print 'STR CONTENT: ' + self.strContent()
                return ''
            index = random.randint(0, self.root.count - 1)
            return self.root.getWord(index)
        
        index = random.randint(0, self.getTotal() - 1)
        stack = []
        if hasattr(self.root, 'uChild'):
            stack.append(self.root.uChild)
        if hasattr(self.root, 'sChild'):
            stack.append(self.root.sChild)

        while(len(stack) > 0):
            current = stack.pop()
            if index < current.count:
                return current.getWord(index)
            index -= current.count
            if hasattr(current, 'uChild'):
                stack.append(current.uChild)
            if hasattr(current, 'sChild'):
                stack.append(current.sChild)
        

    def generateWord(self, stress='*'):
        count = self.getCount(stress)
        if count == 0:
            return self.generateFreeWord()
    
        index = random.randint(0, self.getCount(stress) - 1)
        if stress == '*':
            index = random.randint(0, self.root.count - 1)
            return self.root.getWord(index)
        else:
            current = self.root
            for syl in stress:
                if syl == '0':
                    if hasattr(current, 'uChild'):
                        current = current.getUChild()
                        if index < current.count:
                            return current.getWord(index)
                    else:
                        print 'Unable to match stress'
                        return self.generateWord()
                elif syl == '1':
                    if hasattr(current, 'sChild'):
                        current = current.getSChild()
                        if index < current.count:
                            return current.getWord(index)
                    else:
                        print 'Unable to match stress'
                        return self.generateWord()
                index -= current.count
            print 'Unable to match stress'
            return self.generateWord()
        

def buildLM(tokenLines, n):
    lm = {}
    lm['[START]'] = StressTree('[START]')
    for progress_bar, line in enumerate(tokenLines):
        if len(line) < n:
            continue
        line.append('[END]')
        lm['[START]'].observeWord(' '.join([line[i] for i in range(0, n-1)]))
        for tokenPair in [(' '.join([line[i] for i in range(x, x + n-1)]), line[x + n-1]) \
                              for x in range(0, len(line) - n + 1)]:
            if not lm.has_key(tokenPair[0]):
                lm[tokenPair[0]] = StressTree(tokenPair[0])
            lm[tokenPair[0]].observeWord(tokenPair[1])
        if (progress_bar % 5000) == 0:
            print "Progress: " + str((progress_bar * 100) / len(tokenLines)) + "%"
    return lm

def generateLine(lm, n):
    result = lm['[START]'].generateWord().split()
    while not result[len(result) - 1] == '[END]':
        key = ' '.join([result[i] for i in range(len(result) - n + 1, len(result))])
        if lm.has_key(key):
            result.append(lm[key].generateFreeWord())
        else:
            result.append('[END]')
    return result[:len(result) - 1]

def generateMatchingLines(lm, n, stress):
    result = []
    while len(result) < n - 1:
        result = lm['[START]'].generateWord().split()
    while len(stress) > 0:
        key = ' '.join([result[i] for i in range(len(result) - n + 1, len(result))])
        if lm.has_key(key):
            result.append(lm[key].generateWord(stress))
            stress = stress[len(getStress(result[len(result) - 1])):]
        else:
            stress = ''
        if result[len(result) - 1] == '[END]':
            result = result[:len(result) - 1]
    finalStress = getStress(result[len(result) - 1])
    key = ' '.join([result[i] for i in range(len(result) - n + 1, len(result))])
    iterations = 0
    while (lm.has_key(key) and (not lm[key].root.tokens.has_key('[END]'))) and iterations < 20:
        if not lm.has_key(key):
            result[len(result)-1] = lm[' '.join([result[i] for i in range(len(result) - n, len(result) - 1)])].generateWord(finalStress)
        iterations += 1
    return result

def getStress(word):

    if not ALPHA_EXP.match(word):
        return '*'

    lowercase = word.lower()
    if lowercase not in CMU_DICT:
        return '*'
    else:
        phonemeList = [' '.join([str(c) for c in lst]) for lst in max(CMU_DICT[lowercase])]
        phonemeStr = ''.join(phonemeList)
        stressPattern = ''.join([i for i in phonemeStr if i.isdigit()]).replace('2', '1')
        return stressPattern

def testModel():
    lyricLines = []
    for filename in glob.glob('lyrics/*'):
        print filename
        with codecs.open(filename, 'r', encoding='utf-8') as lyrics:
            lyricLines.extend(lyrics.read().split('\n'))
    tokens = [[word.encode('ascii', 'ignore') for word in line.split()] for line in lyricLines]
    
    lm = buildLM(tokens, 3)

    for i in range(0, 5):
        print "___________________\n"
        line = generateLine(lm, 3)
        while len(line) > 15:
            line = generateLine(lm, 3)
        print line

        stressPattern = ''.join(getStress(word).replace('*', '') for word in line)
        candidateLines = []
        for j in range(0, 12):
            matchingLine = ' '.join(generateMatchingLines(lm, 3, stressPattern))
            candidateLines.append(matchingLine)

        rhymedLines = rhyme.rhyme(candidateLines, 'aabb')
        for i, line in enumerate(rhymedLines):
            print ' '.join(line)
            if (i+1) % 4 == 0:
                print ""



if __name__ == "__main__":

    testModel()

