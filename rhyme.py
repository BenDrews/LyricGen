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
    # Don't rhyme punctuation
    change_index = -1
    rhyme_index = -1
    change_word = ""
    rhyme_word = ""

    # Backtrack to the last non-punctuation word
    while change_word[change_index] in string.punctuation:
        change_index -= 1
    while rhyme_word[rhyme_index] in string.punctuation:
        rhyme_index -= 1
        
    change_word = line1[change_index]
    rhyme_word = line2[rhyme_index]
    prev_word = line1[change_index - 1]
    
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
    return (score, rhymes, change_index)


def makeLinesRhyme(line1, line2):
    # Check whether the better rhyme is A1->A2 or A2->A1
    (line1_score, line1_rhymes, change1_index) = getRhymeWords(line1, line2)
    (line2_score, line2_rhymes, change2_index) = getRhymeWords(line2, line1)

    changed_line = []
    kept_line = []
    rhymes = []
    change_index = -1
    if line1_score >= line2_score:
        # Change the first line to rhyme with the second
        changed_line = line1
        kept_line = line2
        rhymes = line1_rhymes
        change_index = change1_index
    else:
        # Change the second line to rhyme with the first
        changed_line = line2
        kept_line = line1
        rhymes = line2_rhymes
        change_index = change2_index

    # Replace with the closest syllabic match for rhyme in rhymes:
    syllable_count = getSyllableCount(changed_line[change_index])
    best_match_index = 0
    closest_syllables = 10
    for index, rhyme in enumerate(rhymes):
        syllabic_difference = abs(rhyme["numSyllables"] - syllable_count)
        if syllabic_difference == 0:
            changed_line[change_index] = rhyme["word"]
            return (line1, line2)
        elif syllabic_difference < closest_syllables:
            best_match_index = index
            closest_syllables = syllabic_difference

    changed_line[change_index] = rhymes[best_match_index]["word"]
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


if __name__ == "__main__":
    lines = ["I am so blue I'm greener than purple", "Now I'm a cereal killer", "Llamas eat sexy paper clips", "Every day a grape licks a friendly cow"]
    lines.extend(["What is your favorite color of the alphabet", "The sparkly lamp then punched larry", "Look, a distraction", "Screw world peace, I want a pony"])
    lines = rhyme(lines, 'aabb')
