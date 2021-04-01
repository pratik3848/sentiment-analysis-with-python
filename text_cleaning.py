from spellchecker import SpellChecker
import truecase
import re
spell = SpellChecker()

def spellcheck(user_input):
	res=[]
	for word in user_input:
		res.append(spell.correction(word))
	return res

def remove_duplicate_words(user_input):
	#user_input=[word.lower() for word in user_input]

	res=[]
	for index,word in enumerate(user_input):
		try:
			if((word.lower()==user_input[index+1].lower()) or (word.lower()==user_input[index-1].lower())):
				if word not in res:
					res.append(word)
			else:
				res.append(word)
		except:
			res.append(word)
			continue
	return(spellcheck(res))


def remove_special_chars(user_input):
	res=[]
	for word in user_input:
		try:
			if(float(word)):
				res.append(word)
		except:
			res.append(re.sub('[^A-Za-z0-9]+', '', word))
	#print("res inside remove_special_chars:"+str(res))
	return(remove_duplicate_words(res))

def clean(user_input):
	user_input=user_input.replace(',',' ')

	return remove_special_chars(user_input.split())

#print(clean("Great phone with a PHEN###OMENAL Cmera, not! all that hard to get use to. However the screen IS NOT 5.8,it's not all that bigger than my S7 Edge. So maybe a 5.6 screen, it just looks bigger cus it's not as wide as my S7 Edge, takes amazing pictures."))

# user_input="I have been itruly impressed with the new Samsung Galaxy S8 It feels great in my hand. iphone It very easy to read from It is incredibly responsive both to the touch and in changing sites And, of course, the screen and picture on it are outstanding I an a Samsung guy This just helps me to stay one"
# val="Samsung Galaxy S8"
# res=val.lower()
# user_input=user_input.replace("Samsung Galaxy S8",val)

