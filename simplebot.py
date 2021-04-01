from textblob import TextBlob
import twily_classifier as cl
import stop_words as stopwords
import json
import csv
import re
from emosent import get_emoji_sentiment_rank
import string
from flask import Flask,request, jsonify,render_template,Markup
from flask_restful import Resource, Api, reqparse
import pandas as pd
import ast
import sentiment as sn
import words as words
import os.path
#from flask_ngrok import run_with_ngrok




user_excel_df=pd.DataFrame()
u_entity_list=[]
u_csv=''
extension=''
app = Flask(__name__)
#api = Api(app) #for Local server with Flask
#run_with_ngrok(app) for ngrok
app.config["DEBUG"] = True
app.config['JSON_AS_ASCII'] = False

with open('twilybot.json', 'r') as f:
        array = json.load(f)

BOT_NAME = 'Twily'

class sentiments(Resource):
    CONVERSATION = array["conversations"]
    
    STOP_WORDS = stopwords.sw_list
    neg_distribution = []
    def sentiment(self,u_input):
        average_emoji_sentiment={}
        emojis_u_input=u_input
        for c in string.punctuation:
            emojis_u_input= emojis_u_input.replace(c,"")
        emojisFound=re.findall(r'[^\w\s,]', emojis_u_input)
        if emojisFound:
            average_emoji_sentiment=self.getEmojiSentiment(emojisFound)
            for emoji in emojisFound:
                u_input=u_input.replace(emoji, '')
        split_sentiment={'neg': 0.0, 'neu': 0.0, 'pos': 0.0, 'compound': 0.0}
        neighbourhood_sentiment={'neg': 0.0, 'neu': 0.0, 'pos': 0.0, 'compound': 0.0}
        final_sentiment={'neg': 0.0, 'neu': 0.0, 'pos': 0.0, 'compound': 0.0}
        final_sentiment_with_emoji_sentiment={'neg': 0.0, 'neu':0.0 ,'pos': 0.0, 'compound': 0.0}
        entity=cl.getEntity(u_input)
        if len(entity)>0:
            for en in entity:
                result=cl.compile_split_sentiment(u_input,en)
                for key in result.keys():
                    split_sentiment[key]+=result[key]
                answer= cl.compile_neighborhood_sentiment(u_input,en)
                for key in answer.keys():
                    neighbourhood_sentiment[key]+=answer[key]
        else:
            value=cl.getSentiment(u_input)
            for key in value.keys():
                final_sentiment[key]+=value[key]
        if len(entity)>0:
            for key in split_sentiment.keys():
                final_sentiment[key]=(split_sentiment[key]+ neighbourhood_sentiment[key])/2
        if emojisFound:
            final_sentiment_with_emoji_sentiment['neg']=self.Average([final_sentiment['neg'],average_emoji_sentiment['Negative']/100])
            final_sentiment_with_emoji_sentiment['neu']=self.Average([final_sentiment['neu'],average_emoji_sentiment['Neutral']/100])
            final_sentiment_with_emoji_sentiment['pos']=self.Average([final_sentiment['pos'],average_emoji_sentiment['Positive']/100])
            final_sentiment_with_emoji_sentiment['compound']=final_sentiment['compound']
            return final_sentiment_with_emoji_sentiment
        else:
            return final_sentiment
        


    #print(sentiment("That speech influenced her so much that it changed her life"))


    def simplebot(user_input):
        """Rule base bot, takes an argument, user input in form of a string. (truncated)"""
        user_blob = TextBlob(user_input)
        lower_input = user_blob.lower()
        token_input = lower_input.words
        filtered_input = [w for w in token_input if w not in STOP_WORDS]
        response_set = set()
        for con_list in CONVERSATION:
            for sentence in con_list:
                sentence_split = sentence.split()
                if set(filtered_input).intersection(sentence_split):
                    response_set.update(con_list)          
        if not response_set:
            return "I am sorry, I don't have an answer. Ask again please!"
        else:
            return max(response_set, key=len)

    def Average(self,lst): 
        return sum(lst) / len(lst) 

    def getEmojiSentiment(self,emoji_input):
        emoji_sentiment={'Emoji':[],'Negative':[],'Neutral':[],'Positive':[]}
        emoji_sentiment_average={'Negative':'0.0','Neutral':'0.0','Positive':'0.0'}
        list_set = set(emoji_input)
        unique_emojis = (list(list_set))
        for emoji in unique_emojis:
            emoji_sentiment['Negative'].append(get_emoji_sentiment_rank(emoji)['negative'])
            emoji_sentiment['Neutral'].append(get_emoji_sentiment_rank(emoji)['neutral'])
            emoji_sentiment['Positive'].append(get_emoji_sentiment_rank(emoji)['positive'])
            emoji_sentiment['Emoji'].append(emoji)
        if(len(emoji_sentiment['Emoji']) > 1):
            emoji_sentiment_average['Negative'] = self.Average(emoji_sentiment['Negative'])
            emoji_sentiment_average['Neutral'] = self.Average(emoji_sentiment['Neutral']) 
            emoji_sentiment_average['Positive'] = self.Average(emoji_sentiment['Positive'])
        else:
            emoji_sentiment_average['Negative'] = emoji_sentiment['Negative'][0]
            emoji_sentiment_average['Neutral'] = emoji_sentiment['Neutral'][0]
            emoji_sentiment_average['Positive'] = emoji_sentiment['Positive'][0]
        return emoji_sentiment_average


    def escalation(self,user_input):
        live_rep = f"We apologize {BOT_NAME} is unable to assist you, we are getting a live representative for you, please stay with us ..."
        new_dict={'Sentence':"",'Negative':0.0,'Neutral':0.0,'Positive':0.0,'Compound':0.0}
        new_dict['Sentence']=user_input
        mydict=self.sentiment(user_input)
        filename = "data.csv"
        new_dict['Negative']=mydict['neg']
        new_dict['Neutral']=mydict['neu']
        new_dict['Positive']=mydict['pos']
        new_dict['Compound']=mydict['compound']
        with open('data.csv', 'a' ,encoding="utf8") as csvfile:
        	fieldnames = ['Sentence','Negative','Neutral','Positive','Compound']
        	writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        	writer.writerow(new_dict)
        return new_dict

# @app.route('/sentiments/<u_input>', methods=['GET'])
# def home(u_input):
#     object = sentiments()
#     new_dict=object.escalation(u_input)
#     return jsonify(new_dict)

@app.route('/', methods=['GET'])
def index() :
    return render_template('index.html')
  
@app.route('/', methods=['POST'])
def getUserInput():
    u_input=request.form['user_input']
    if u_input:
        object = sentiments()
        new_dict=object.escalation(u_input)
        return render_template('index.html',s=new_dict['Sentence'],n=new_dict['Negative'],neu=new_dict['Neutral'],p=new_dict['Positive'],c=new_dict['Compound'])
    else:
        return render_template('index.html',no="You have not entered any sentence!")

@app.route('/main', methods=['GET'])
def redirectToCSV():
    return render_template('index2.html')

@app.route('/csv', methods=['POST'])
def redirectToCSV1():
    global user_excel_df
    global u_csv
    global u_entity_list
    global extension
    u_csv=request.files['usercsv']
    if u_csv:
        extension = u_csv.filename
        if extension.endswith('.csv') or extension.endswith('.xlsx') or extension.endswith('.xlsm') or extension.endswith('.xls'):
            user_excel_df=pd.read_csv(u_csv, encoding='cp437',error_bad_lines=False, engine='python',names=['Data'])
            print(user_excel_df)
            return render_template('index2.html',uploaded="Successfully Uploaded")
        else:
            extension=''
            u_entity_list=[]
            u_csv=''
            return render_template('index2.html',wrongformat="Please upload the file in Excel format")
    elif not u_csv and user_excel_df.empty :
        return render_template('index2.html',nocsv="You have not uploaded any csv file!")
    elif not u_csv and not user_excel_df.empty:
         return render_template('index2.html',uploaded="You have already uploaded a file : " +extension + Markup("<br>" +  "Please choose new to upload a new file"))

@app.route('/entities', methods=['POST'])
def getEntity():
    global u_entity_list
    global extension
    u_entity_list=[]
    sn.sentiment_required=[]
    u_entity=request.form['userentity']
    u_entity_list=u_entity.split(',')
    if u_entity:
        if len(u_entity_list)>1 and ',' not in u_entity:
            return render_template('index2.html',comma="Please enter comma seperated values")
        elif len(u_entity_list)==1:
            sn.sentiment_required=u_entity_list
            return render_template('index2.html',yourEntity="Your Entity:"+u_entity,uploaded=extension)
        else:
            sn.sentiment_required=u_entity_list
            return render_template('index2.html',yourEntity="Your Entities:"+u_entity,uploaded=extension)

    else:
        u_entity_list=[]
        return render_template('index2.html',no="You have not entered any entity!",uploaded=extension)

@app.route('/getSentiment', methods=['POST'])
def getFinalSentiment():
    global u_entity_list
    global user_excel_df
    global extension
    final_sentiment=''
    if (not user_excel_df.empty) and u_entity_list:
        result_dict=sn.getUserExcel(user_excel_df)
        for key,value in result_dict.items():
            final_sentiment+="Sentiment for " + str(key)+ "- "+ "Negative: " + str(value['neg']) + " Neutral: " + str(value['neu']) + " Positive: " + str(value['pos']) + "<br>"
        final_sentiment = Markup(final_sentiment)
        if(result_dict):
            return render_template('index2.html',final_result=final_sentiment,uploaded=extension,yourEntity="Your Entities:"+str(','.join(u_entity_list)))
        else:
            return render_template('index2.html',final_result_no="Word not found")
    elif  user_excel_df.empty or not u_entity_list:
        final_sentiment=''
        result_dict={}
        sn.sentiment_required=[]
        return render_template('index2.html',nothing="You have not entered the above fields!")


if __name__ == '__main__':
    app.run()



