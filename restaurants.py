import nltk
from nltk.tag import pos_tag
import requests
import json
import pandas as pd
import simplebot as sb
import twily_classifier as cl
import phrase_catcher as pc
import stop_words as stopwords
from geotext import GeoText
from geograpy.extraction import Extractor
#nltk.download('maxent_ne_chunker')
#nltk.download('words')
import geograpy
import spacy
import text_cleaning as tc






api_key="24f7e4be7d0397aad12e529ca1c293f5"
api_endpoint="https://developers.zomato.com/api/v2.1/"
header = {"Accept": "application/json", "user_key": api_key}
restaurant_categories={'delivery':'1','dine-out':'2','dineout':'2','nightlife':'3','catching-up':'4','catchingup':'4','takeaway':'5','cafes':'6','cafe':'6','daily menus':'7','breakfast':'8'
,'lunch':'9','dinner':'10','pubs & bars':'11','pubs':'11','bars':'11','pocket friendly delivery':'12','clubs & lounges':'14','clubs':'14','club':'14','lounge':'14'}

STOP_WORDS = stopwords.restaurant_stop_words
restaurant_details={}
df_name=""
result_dict={}
final_dict={}
result_dict['location_suggestions_dataframe']=pd.DataFrame()
result_dict['restaurants_dataframe']=pd.DataFrame()
result_dict['cuisines_dataframe']=pd.DataFrame()
result_dict['establishments_dataframe']=pd.DataFrame()
api_call_dict={'entity_id=':"",'entity_type=':"",'category=':'','collection_id=':'','establishment_type=':"",'cuisines=':"",'sort=':'','order=':'','q=':"",'count=':'5'}
response_object_location={'location':0,'search':3}
tagged_sent={}
updated_user_input=[]

def getDetails(response,loc):
	global df_name
	global result_dict
	global final_dict
	single_item={}
	df=str(str(df_name)+"_dataframe")
	response_details=response[list(response.keys())[loc]]
	for info in response_details:
		for key,value in info.items():
			if(type(value) is not dict):
				if not key in single_item.keys():
					single_item[key]=value
				else:
					key=key+"_"+value
					single_item[key]=value
			else:
				single_item=getNestedValues(value,single_item,key)
			final_dict.update(single_item)
			single_item={}
		result_dict[df]=result_dict[df].append(final_dict,ignore_index=True)
	final_dict={}

def getNestedValues(nestedDict,single_item,key1):
	for key,value in nestedDict.items():
		if(type(value) is not dict):
			if not key in single_item.keys():
				single_item[key]=value
			else:
				key=key+"_"+key1
				single_item[key]=value
		else:
			getNestedValues(value,single_item,key)
	return single_item

def update_count_value():
	global api_call_dict
	global updated_user_input
	nlp = spacy.load('en_core_web_lg')
	tagged_sent = pos_tag(updated_user_input)
	tagged_sent=dict(tagged_sent)
	words=[]
	for key,value in tagged_sent.items():
		if(value not in ['NNP','NN']):
			words.append(key)
	best=nlp('best')
	if(len(words)>0):
		for index,word in enumerate(words):
			if(str(word).isalpha()):
				val=nlp(word) 
				if(val.similarity(best) >= 0.46):
					updated_user_input.remove(word)
					try:
						if(words[index+1].isdigit()):
							api_call_dict['count=']=words[index+1]
							updated_user_input.remove(words[index+1])
						elif(words[index-1].isdigit()):
							api_call_dict['count=']=words[index-1]
							updated_user_input.remove(words[index-1])
					except:
						#res=[for word in updated_user_input if word.isalpha()]
						api_call_dict['count=']=5

def update_api_call_dict(user_input):
	global tagged_sent
	global df_name
	global api_call_dict
	global updated_user_input
	global updated_user_input
	search_parameter=""

	api_call_dict['entity_id=']=str(round(result_dict['location_suggestions_dataframe'].iloc[0]['entity_id']))+"&"
	api_call_dict['entity_type=']=str(result_dict['location_suggestions_dataframe'].iloc[0]['entity_type'])+"&"
	cuisine_names=list(result_dict['cuisines_dataframe']['cuisine_name'])
	establishments_name=list(result_dict['establishments_dataframe']['name'])
	update_count_value()
	updated_user_input=[word for word in updated_user_input if word.lower() not in STOP_WORDS]
	updated_user_input_temp=updated_user_input.copy()
	for word in updated_user_input_temp:
		if(word.capitalize() in cuisine_names):
			res=result_dict['cuisines_dataframe'].loc[result_dict['cuisines_dataframe']['cuisine_name']==word.capitalize()]
			cuisine_id=round(res['cuisine_id'].tolist()[0])
			api_call_dict['cuisines=']=str(cuisine_id)+"&"
			updated_user_input.remove(word)
		elif(word.capitalize() in establishments_name):
			res=result_dict['establishments_dataframe'].loc[result_dict['establishments_dataframe']['name']==word.capitalize()]
			establishment_id=round(res['id'].tolist()[0])
			api_call_dict['establishment_type=']=str(establishment_id)+"&"
			updated_user_input.remove(word)
		elif(word.capitalize() in list(restaurant_categories.keys())):
			api_call_dict['category=']=str(restaurant_categories[word])+"&"
			updated_user_input.remove(word)

	# if(len(updated_user_input)>0):
	# 	updated_user_input=[word for word in updated_user_input if word.isalpha()]
	# 	api_call_dict['q=']=" ".join(updated_user_input)+"&"
	# sent_dict=sb.sentiment(user_input)
	# if(sent_dict['pos']>= sent_dict['neu']):
	# 	api_call_dict['order=']="desc&"
	# 	api_call_dict['sort=']='rating&'
			
def get_location_details(word):
	global df_name
	global api_call_dict
	response = requests.get(api_endpoint+"locations?query="+word, headers=header)
	response=response.json()
	df_name=str(list(response.keys())[0])
	getDetails(response,0)

def get_cusine_details(location):
	global df_name
	api_endpoint="https://developers.zomato.com/api/v2.1/cuisines?city_id="
	city_id=str(result_dict['location_suggestions_dataframe'].iloc[0]['city_id'])
	response = requests.get(api_endpoint+city_id,headers=header)
	response=response.json()
	df_name=str(list(response.keys())[0])
	getDetails(response,0)

def get_establishment_details(location):
	global df_name
	api_endpoint="https://developers.zomato.com/api/v2.1/establishments?city_id="
	city_id=str(result_dict['location_suggestions_dataframe'].iloc[0]['city_id'])
	response = requests.get(api_endpoint+city_id,headers=header)
	response=response.json()
	df_name=str(list(response.keys())[0])
	getDetails(response,0)




def check_validity(user_input):
	global tagged_sent
	global updated_user_input
	tagged_sent = pos_tag(user_input.split())
	tagged_sent=dict(tagged_sent)
	for key,value in tagged_sent.items():
		if(value != 'NNP'):
			updated_user_input.append(key)
	nouns=[k for k,v in tagged_sent.items() if v == 'NNP']
	cities=[]
	for i in range(len(nouns)):
		ifcity=nouns[i]
		places = geograpy.get_geoPlace_context(text=ifcity)
		if places.cities:
			cities.append(places.cities)
		else:
			updated_user_input.append(ifcity)
	if(len(cities)==1):
		city=str(cities[0][0])
		get_location_details(city)
		get_cusine_details(city)
		get_establishment_details(city)
		return True
	else:
		#print("please enter a query with city name")
		return False

def form_api():
	endpoint=api_endpoint+"search?"
	global api_call_dict
	for key,value in api_call_dict.items():
		if(len(str(value))>0):
			endpoint+=(str(key) + str(value))
	return endpoint


def form_output(r):
	result=result_dict['restaurants_dataframe'].name
	output=""
	for val in result:
		output+=val + "\n"
	return output + r.text


s=requests.Session()
setCookieUrl="https://httpbin.org/cookies/set"
getCookiesUrl="https://httpbin.org/cookies/set"

def final_api_call(user_input):
	global df_name
	global api_call_dict
	global updated_user_input
	user_input=tc.clean(user_input)
	print(user_input)
	para=user_input[0]
	user={'user':'para'}
	if(check_validity(user_input)):
		update_api_call_dict(user_input)
		endpoint=form_api()
		print(endpoint)
		response = requests.get(endpoint, headers=header)
		response=response.json()
		df_name=str(list(response.keys())[3])
		getDetails(response,3)
		r=s.get(getCookiesUrl)
		s.get(setCookieUrl,params=user)
		return form_output(r)
	else:
		return "Please enter a query with city name"


#print(final_api_call("find me top 10 chinese bar  in pune "))
def find_answer(user_input):
	return(final_api_call(user_input))

#print(result_dict['establishments_dataframe'])
# print(result_dict['cuisines_dataframe'])





