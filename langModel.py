import sys, getopt, nltk, re, string, random, codecs, glob, datamuse, pronouncing
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

# The api object used to access the rhyming database
api = datamuse.Datamuse()

def getSyllableCount(word):
    # Return the number of syllables
    phones = pronouncing.phones_for_word(word)
    return pronouncing.syllable_count(phones[0])


def getRhymeWords(line1, line2):
    change_word = line1[-1]
    prev_word = line1[-2]
    rhyme_word = line2[-1]
    
    # Get semantically related and rhyming words that typically follow the previous word
    score = 3
    rhymes = api.words(rel_rhy=rhyme_word, ml=change_word, lc=prev_word)
    rhymes.extend(api.words(rel_nry=rhyme_word, ml=change_word, lc=prev_word))
    if (len(rhymes) == 0):
        # Otherwise, get words that rhyme with the second word and are semantically related
        score -= 1
        rhymes = api.words(rel_rhy=rhyme_word, ml=change_word, lc=prev_word)
        rhymes.extend(api.words(rel_nry=rhyme_word, ml=change_word, lc=prev_word))
        if len(rhymes) == 0:
            # Otherwise, get words that rhyme and follow the previous word
            score -= 1
            rhymes = api.words(rel_rhy=rhyme_word, lc=prev_word, max=10)
            rhymes.extend(api.words(rel_nry=rhyme_word, lc=prev_word, max=10))
            if (len(rhymes) == 0):
                # Otherwise, get words that rhyme 
                score -= 1
                rhymes = api.words(rel_rhy=rhyme_word, max=10)
                rhymes.extend(api.words(rel_nry=rhyme_word, max=10))

    print (change_word + " to " + rhyme_word + " ----- " + str(score) + " : " + str(rhymes) + "\n\n\n")
    return (score, rhymes)


def makeLinesRhyme(line1, line2):
    # Check whether the better rhyme is A1->A2 or A2->A1
    (line1_score, line1_rhymes) = getRhymeWords(line1, line2)
    (line2_score, line2_rhymes) = getRhymeWords(line2, line1)

    changed_line = []
    kept_line = []
    rhymes = []
    if line1_score >= line2_score:
        # Change the first line to rhyme with the third
        changed_line = line1
        kept_line = line2
        rhymes = line1_rhymes
    else:
        # Change the third line to rhyme with the first
        changed_line = line2
        kept_line = line1
        rhymes = line2_rhymes

    # Replace with the closest syllabic match for rhyme in rhymes:
    syllable_count = getSyllableCount(changed_line[-1])
    best_match_index = 0
    closest_syllables = 10
    for index, rhyme in enumerate(rhymes):
        syllabic_difference = abs(rhyme["numSyllables"] - syllable_count)
        if syllabic_difference == 0:
            changed_line[-1] = rhyme["word"]
            return (line1, line2)
        elif syllabic_difference < closest_syllables:
            best_match_index = index
            closest_syllables = syllabic_difference

    changed_line[-1] = rhymes[best_match_index]["word"]
    return (line1, line2)
    

def rhyme(lines, scheme):
    result = []
    # Consider four lines at a time
    for four_tuple in zip(*[iter(lines)]*4):
        (a, b, c, d) = (x.split(' ') for x in four_tuple)

        # ABAB rhyme scheme
        if scheme == "abab":
            (a, c) = makeLinesRhyme(a, c)
            (b, d) = makeLinesRhyme(b, d)
        elif scheme == "aabb":
            (a, b) = makeLinesRhyme(a, b)
            (c, d) = makeLinesRhyme(c, d)
        else:
            print "Invalid rhyme scheme"
            return

        # Add rhymed tuple to results
        result.extend([a, b, c, d])
        
    return result


def buildLM(tokenLines, n):
    lm = {}
    lm['[START]'] = StressTree('[START]')
    for line in tokenLines:
        if len(line) < n:
            continue
        line.append('[END]')
        lm['[START]'].observeWord(' '.join([line[i] for i in range(0, n-1)]))
        for tokenPair in [(' '.join([line[i] for i in range(x, x + n-1)]), line[x + n-1]) \
                              for x in range(0, len(line) - n + 1)]:
            if not lm.has_key(tokenPair[0]):
                lm[tokenPair[0]] = StressTree(tokenPair[0])
            lm[tokenPair[0]].observeWord(tokenPair[1])
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
    tokens = [[word.encode('ascii', 'ignore') for word in nltk.wordpunct_tokenize(line)] for line in lyricLines]
    
    lm = buildLM(tokens, 3)
    print lm['[START]'].root.tokens.keys()

    for i in range(0, 5):
        print "___________________"
        line = generateLine(lm, 3)
        print line
        stressPattern = ''.join(getStress(word).replace('*', '') for word in line)
        candidateLines = []
        for j in range(0, 10):
            matchingLine = generateMatchingLines(lm, 3, stressPattern)
            print matchingLine
            candidateLines.append(matchingLine)
        rhymedLines = rhyme(candidateLine, 'abab')
        print "RHYMED LINES:"
        for line in rhymedLines:
            print rhymedLines



if __name__ == "__main__":

    testModel()

