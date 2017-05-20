import requests
import datamuse
import pronouncing

api = datamuse.Datamuse()
word = 'lights'

near_rhymes = api.words(rel_nry=word, max=200)
num_syllables = pronouncing.phones_for_word(word)
print ("\n\n\nNear Rhyme")
for rhyme in near_rhymes:
    phones = pronouncing.phones_for_word(rhyme)
    syllables = pronouncing.syllable_count(phones[0])
    if (abs(num_syllables - syllables) <= 1):
        print "\t" + rhyme["word"]

rhymes_meaning = api.words(rel_nry='listening',  ml="listening")
print "\n\n\nRhyme and Meaning:"
print rhymes_meaning

rhymes = api.words(rel_rhy=word, max=20)
print ("\n\n\nPerfect Rhyme") 
