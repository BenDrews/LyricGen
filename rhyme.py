# Joseph Oh
import datamuse
import pronouncing
import requests

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
    
    # Get semantically related and rhyming words that typically follow the 2nd-to-last word
    rhymes = api.words(rel_rhy=rhyme_word, ml=change_word, lc=prev_word)
    rhymes.extend(api.words(rel_nry=rhyme_word, ml=change_word, lc=prev_word))
    score = 3
    if (len(rhymes) == 0):
        # Otherwise, get words that rhyme with the second word and are semantically related
        rhymes = api.words(rel_rhy=rhyme_word, ml=change_word, lc=prev_word)
        rhymes.extend(api.words(rel_nry=rhyme_word, ml=change_word, lc=prev_word))
        score = 2
        if len(rhymes) == 0:
            # Otherwise, get words that rhyme and follow the previous word
            rhymes = api.words(rel_rhy=rhyme_word, lc=prev_word)
            rhymes.extend(api.words(rel_nry=rhyme_word, lc=prev_word))
            score = 1
            if (len(rhymes) == 0):
                # Otherwise, get words that rhyme 
                rhymes = api.words(rel_rhy=rhyme_word)
                rhymes.extend(api.words(rel_nry=rhyme_word))
                score = 0

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

    # Replace with the perfect syllabic match for rhyme in rhymes:
    for rhyme in rhymes:
        if rhyme["numSyllables"] == getSyllableCount(changed_line[-1]):
            changed_line[-1] = rhyme["word"]
            return (line1, line2)

    # Otherwise, return closest syllabic match
    changed_line[-1] = rhymes[0]["word"]
    return (line1, line2)
    

def rhyme(lines):
    result = []
    # Consider four lines at a time
    for four_tuple in zip(*[iter(lines)]*4):
        (a, b, c, d) = (x.split(' ') for x in four_tuple)

        # ABAB rhyme scheme
        (a, c) = makeLinesRhyme(a, c)
        (b, d) = makeLinesRhyme(b, d)

        # Add rhymed tuple to results
        result.extend([a, b, c, d])
        
    return result


if __name__ == "__main__":
    lines = ["these are the days of elijah", "declaring the word of the lord", "these are the days of great trials", "carry my soul, carry my soul away"]
    lines = rhyme(lines)
    for line in lines:
        print line
