import nltk
nltk.download('vader_lexicon')
from nltk.corpus import wordnet 
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.tag import pos_tag
from PyDictionary import PyDictionary
import re
import string



dictionary=PyDictionary()
analyzer = SentimentIntensityAnalyzer()
chars = re.escape(string.punctuation)
emotion_syn=['feeling','sentiment','sensation','reaction','response','passion','intensity','warmth','ardour','fervour','vehemence','fire','excitement','spirit','soul','instinct','sentimentality']


def getSentiment(sentence):
	return analyzer.polarity_scores(sentence)

def getEntity(sentence):
    entity=[]
    tagged_sent = pos_tag(sentence.split())
    for word,pos in tagged_sent:
        var=word
        if (pos == 'NN' or pos == 'NNP' or pos == 'NNS' or pos == 'NNPS'):
            dict_meaning=dictionary.meaning(word)
            if(dict_meaning):
                res=[v for k, v in dict_meaning.items()]
                count=0
                for item in res:
                    for x in item:
                        for i in x.split():
                            if i in emotion_syn:
                                count=1
                                break
                if count==0:
                    entity.append(var)
            else:
                entity.append(var)      
    return entity   


def compile_neighborhood_sentiment(sentence, entity, decay = 0.5, propagation = 5):
    '''
    Find instances of entity in sentence. Add sentiment of neighboring words. Incrementally expand neighborhood
    up to limit set by propagation variable. Add up sentiment with decay as neighborhood expands.
    '''
    first_sent = 0
    compiled_sentiment = {'neg': 0.0, 'neu': 0.0, 'pos': 0.0, 'compound': 0.0}

    sentence = sentence.lower().replace(',', '').split(' ')

    sen_len = len(sentence)
    ent_locs = []

    # Find locations of entity within sentence
    for i, word in enumerate(sentence):
        if word == entity.lower():
            ent_locs.append(i)

    # how many entity locations there are
    n_locs = len(ent_locs)

    # Only execute rest of function if word is actually in sentence
    if n_locs != 0:

        # Iterate through propagation parameter
        for i in range(propagation):
            neighborhoods = []

            # Compile list of entity neighborhoods
            for loc in ent_locs:
                exp_locs = list(range(loc-i-1,loc+i+2))
                neigh = []
                # Only add locations to neighborhoods that are actually in the sentence
                for j in exp_locs:
                    if j >= 0 and j < sen_len:
                        neigh.append(sentence[j])
                # Join all words in neighborhood then add to neighborhoods list
                neigh = ' '.join(neigh)
                # Remove entity
                neigh = neigh.replace(entity.lower(), '')

                neighborhoods.append(neigh)

            # Get average sentiment for all neighborhoods
            sentiment = {'neg': 0.0, 'neu': 0.0, 'pos': 0.0, 'compound': 0.0}

            for neigh in neighborhoods:
                neigh_sent = analyzer.polarity_scores(neigh)
                # Add up sentiments
                for key in sentiment.keys():
                    sentiment[key] += neigh_sent[key]

            # Divide by n_locs to get average
            for key in sentiment.keys():
                sentiment[key] = sentiment[key] / n_locs

            # Compile into main sentiment
            if first_sent == 1:
                weight = (decay)**(i - first_sent_level)
                for key in compiled_sentiment.keys():
                    compiled_sentiment[key] = (compiled_sentiment[key] + sentiment[key] * weight) / (1 + weight)

            if first_sent == 0 and sentiment['neu'] < 0.9:
                if sum(sentiment.values()) != 0:
                    first_sent = 1
                    first_sent_level = i
                    compiled_sentiment = sentiment

    return compiled_sentiment


def compile_split_sentiment(sentence, entity):
    '''
    Split the sentence by comparison words and commas. Determine which sections the entity is in.
    Return average sentiment for those sections.
    '''
    # List of comparison words
    comp_words = ['but', 'however', 'albeit', 'although', 'in contrast', 'in spite of', 'though', 'on one hand', 'on the other hand',
                  'then again', 'even so', 'unlike', 'while', 'conversely', 'nevertheless', 'nonetheless', 'notwithstanding', 'yet']

    # Lowercase sentence and split on commas
    sentence = sentence.lower()
    sentence = sentence.split(',')

    # Iterate through sections and split them based on comparison words
    splits = []
    for section in sentence:

        all_comps = []
        for word in comp_words:
            # Use find all function to find location of comparison words
            all_comps += list(find_all(section, word))

        # Sort list of comparison words indexes
        all_comps.sort()

        # Split the section and append to splits
        last_split = 0
        for comp in all_comps:
            splits.append(section[last_split:comp])
            last_split = comp
        splits.append(section[last_split:])

    # Find the sections where the entity has been named
    # Add sentiment for that section to list
    sentiments = []
    for section in splits:
        if entity.lower() in section:
            # remove entity from section
            cleaned_section = section.replace(entity.lower(), '')
            sentiments.append(analyzer.polarity_scores(cleaned_section))

    # Add sentiment for each section up
    compiled_sentiment = {'neg': 0.0, 'neu': 0.0, 'pos': 0.0, 'compound': 0.0}
    for sentiment in sentiments:
        for key in compiled_sentiment.keys():
            compiled_sentiment[key] += sentiment[key]

    # Divide all sections by lenth of sentiments list to get average
    denom = len(sentiments)
    if denom != 0:
        for key in compiled_sentiment.keys():
            compiled_sentiment[key] = compiled_sentiment[key] / denom

    return compiled_sentiment

def find_all(a_str, sub):
    '''
    Find all matches of sub within a_str. Returns starting index of matches.
    '''
    start = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1: return
        yield start
        start += len(sub) # use start += 1 to find overlapping matches


