import nltk
nltk.download('wordnet')
from nltk.corpus import wordnet   #Import wordnet from the NLTK
syn = list()
ant = list()
for synset in wordnet.synsets("passion"):
	for lemma in synset.lemmas():
		syn.append(lemma.name())
		if lemma.antonyms():
			ant.append(lemma.antonyms()[0].name())
print('Synonyms: ' + str(syn))
print('Antonyms: ' + str(ant))
