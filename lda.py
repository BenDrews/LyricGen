# Justin Smilan, Ben Drews, Joseph Oh

from nltk.tokenize import RegexpTokenizer
from stop_words import get_stop_words
from nltk.stem.porter import PorterStemmer
import glob, os, codecs

# Global variables
docs = []
clean_list = []

def tokenize(line_list):
    # Tokenize the document
    for i, line in enumerate(line_list):
        line_list[i] = line.split(' ')
    return line_list
    

def removeStopWords(tokens_list):
    # List of English stop words
    stop_words = get_stop_words('en')
    # Remove stop words from doc
    for i, tokens in enumerate(tokens_list):
        tokens_list[i] = [x for x in tokens if x not in stop_words]
    return tokens_list


def stem(tokens_list):
    # Stem the tokens in doc
    p_stemmer = PorterStemmer()
    for i, tokens in enumerate(tokens_list):
        tokens_list[i] = [p_stemmer.stem(x) for x in tokens]
    return tokens_list


def clean(docs):
    # Clean each document
    for i, doc in enumerate(docs):
        line_list = doc.split('\n')
        tokens_list = tokenize(line_list)
        stopped_tokens = removeStopWords(tokens_list)
        stemmed_tokens = stem(stopped_tokens)
        docs[i] = stemmed_tokens
        for token_list in stemmed_tokens:
            line = ""
            for token in token_list:
                line += token + " "
            print line


if __name__ == "__main__":
    # Gather all the lyric files
    docs = []
    for filename in glob.glob('lyrics/*'):
        with codecs.open(filename, 'r', encoding='utf-8') as lyrics:
            docs.append(lyrics.read())
            break

    clean(docs)
        
