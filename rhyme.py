# Joseph Oh
import datamuse
import pronouncing
import requests

api = datamuse.Datamuse()

def getRhymes(change_word, rhyme_word):
    # Get words related to original word that rhymes with second word
    rhymes = api.words(rel_nry=rhyme_word, ml=change_word, max=20)
    rhymes.extend(api.words(rel_rhy=rhyme_word, ml=change_word, max=20))
    cohesive = True

    # Otherwise, get words that rhyme with the second word
    if (len(rhymes) == 0):
        rhymes = api.words(rel_rhy=rhyme_word, max=10)
        cohesive = False
        if (len(rhymes) == 0):
            rhymes = api.words(rel_nry=rhyme_word, max=10)
        
    return (cohesive, rhymes)
    

def makeRhymes(lines):
    result = []
    # Consider four lines at a time
    for four_tuple in zip(*[iter(lines)]*4):
        (a, b, c, d) = (x.split(' ') for x in four_tuple)

        # Check whether the better rhyme is A1->A2 or A2->A1
        (a1_cohesive, a1_rhymes) = getRhymes(a[-1], c[-1])
        (a2_cohesive, a2_rhymes) = getRhymes(c[-1], a[-1])

        if a1_cohesive:
            # Change the first line to rhyme with the third
            a[-1] = a1_rhymes[0]
        else:
            # Change the third line to rhyme with the first
            c[-1] = a2_rhymes[0]

        print str(a) + " : " + str(c)
        
    return result


if __name__ == "__main__":
    lines = ["hello this is bob", "what a beautiful world", "for a long time there is nothing", "here we go again time's up"]
    lines = makeRhymes(lines)
    for line in lines:
        print line
