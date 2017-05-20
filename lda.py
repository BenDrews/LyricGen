# Justin Smilan, Ben Drews, Joseph Oh
from gensim import corpora, models
from nltk.tokenize import RegexpTokenizer
from stop_words import get_stop_words
from nltk.stem.porter import PorterStemmer
import glob, os, codecs, gensim, string

# Global variables
docs = []
clean_list = []

def tokenize(doc):
    # Tokenize the document
    return doc.split()

def removeStopWords(tokens):
    # List of English stop words
    stop_words = get_stop_words('en')
    stop_words.extend(set(string.punctuation))
    # Remove stop words from doc
    return [x for x in tokens if x not in stop_words]


def stem(tokens):
    # Stem the tokens in doc
    p_stemmer = PorterStemmer()
    return [p_stemmer.stem(x) for x in tokens]


def clean(docs):
    # Clean each document
    for i, doc in enumerate(docs):
        tokens = tokenize(doc)
        stopped_tokens = removeStopWords(tokens)
        stemmed_tokens = stem(stopped_tokens)
        docs[i] = stemmed_tokens


def constructMatrix(docs):
    # Create a Document-term matrix
    dictionary = corpora.Dictionary(docs)
    corpus = [dictionary.doc2bow(doc) for doc in docs]

    # Generate an LDA model
    ldamodel = gensim.models.ldamodel.LdaModel(corpus, num_topics=5, id2word = dictionary, passes=20)
    print(ldamodel.print_topics(num_topics=5, num_words=3))


if __name__ == "__main__":
    # Gather all the lyric files
    docs = []
    i = 0
    for filename in glob.glob('lyrics/*'):
        i += 1
        if i > 10:
            break
        with codecs.open(filename, 'r', encoding='utf-8') as lyrics:
            docs.append(lyrics.read())

    clean(docs)
    constructMatrix(docs)
    
