import words as words
import nltk
#nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import text_cleaning as tc
from PyDictionary import PyDictionary
dictionary=PyDictionary()


analyzer = SentimentIntensityAnalyzer()
sentiment_required=[]
result_dict=dict()
all_entity=[]
def validate_entity_locations(exp_locs,remaining_entities_index,loc):
    res=[]
    entity_index=loc
    flag=0
    if(len(remaining_entities_index)>0):
        for loc in exp_locs:
            if(flag==0):
                for ent in remaining_entities_index:
                    if((loc<ent) and (loc not in res)):
                        res.append(loc)
                    elif(loc==ent):
                        if(entity_index in res):
                            flag=1
                            break
                        else:
                            res.clear()
                    else:
                        if(loc not in res):
                            res.append(loc)

    entity_location=[val for val in res if val not in remaining_entities_index]
    if(len(entity_location)>0):
        return entity_location
    else:
        return exp_locs


def compile_neighborhood_sentiment(sentence, entity, decay = 0.5, propagation = 6):
    '''
    Find instances of entity in sentence. Add sentiment of neighboring words. Incrementally expand neighborhood
    up to limit set by propagation variable. Add up sentiment with decay as neighborhood expands.
    '''
    global all_entity
    sentence = sentence.replace(',', '').split(' ')
    remaining_entities=[val for val in all_entity if val!=entity]
    if(len(remaining_entities)==0):
        propagation=(len(sentence)//2)+1
    remaining_entities_index=[]

    for index,word in enumerate(sentence):
        for ent in remaining_entities:
            if(word.lower()==ent.lower()):
                remaining_entities_index.append(index)

    first_sent = 0
    compiled_sentiment = {'neg': 0.0, 'neu': 0.0, 'pos': 0.0, 'compound': 0.0}
    sen_len = len(sentence)
    ent_locs = []


    # Find locations of entity within sentence depending on number of words in entity
    for i, word in enumerate(sentence):
        if word.lower() == entity.lower():
            ent_locs.append(i)
    
    # how many entity locations there are
    n_locs = len(ent_locs)
    # Only execute rest of function if word is actually in sentence
    if n_locs != 0:
        #calculate sentiment only one time for each sentence
        neighborhoods_check=[]
        for i in range(propagation):
            neighborhoods = []
            # Compile list of entity neighborhoods
            for loc in ent_locs:
                exp_locs = list(range(loc-i-1,loc+i+2))
                final_entity_locations=validate_entity_locations(exp_locs,remaining_entities_index,loc)
                # Only add locations to neighborhoods that are actually in the sentence
                neigh=[]
                for j in final_entity_locations:
                    if j >= 0 and j < sen_len:
                        neigh.append(sentence[j])

                neigh=[word for word in neigh if word.lower()!=entity]
                neigh = ' '.join(neigh)
                if(neigh not in neighborhoods_check):
                    neighborhoods.append(neigh)
                    neighborhoods_check.append(neigh)

            # Get average sentiment for all neighborhoods
            sentiment = {'neg': 0.0, 'neu': 0.0, 'pos': 0.0, 'compound': 0.0}
            #calculate sentiment only if its not been calculated before
            if(len(neighborhoods)>0):
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

                if first_sent == 0:
                    if sum(sentiment.values()) != 0:
                        first_sent = 1
                        first_sent_level = i
                        compiled_sentiment = sentiment
    return compiled_sentiment  

def getEntity(sentence):
    entity=[]
    sentence=sentence.lower()
    for word in sentiment_required:
        if(word.lower() in sentence):
            entity.append(word)
    return entity

def getUserExcel(userDataframe):
    global result_dict
    result_dict={}
    for index, row in userDataframe.iterrows():
        user_input=tc.clean(str(row[0]))
        user_input=' '.join(user_input)
        all_entity=getEntity(user_input)
        if(len(all_entity)>0):
            for word in all_entity:
                if(len(word.split())>1):
                    word_replace="-".join(word.split())
                    user_input_word_replaced+=user_input.replace(word,word_replace)
                    result_dict[word]=compile_neighborhood_sentiment(user_input_word_replaced,word_replace)
                elif(len(word.split())==1):
                    user_input_splitted=user_input.lower().split()
                    if(word.lower() in user_input_splitted):
                        result_dict[word]=compile_neighborhood_sentiment(user_input,word)
                else:
                    result_dict[word]=compile_neighborhood_sentiment(user_input,word)
    return result_dict


