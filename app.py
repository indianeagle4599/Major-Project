import random
import nltk 
import string
import re
import unicodedata
import pickle

nltk.download('stopwords') 
nltk.download('wordnet') 

stopword = nltk.corpus.stopwords.words('english')
wn = nltk.WordNetLemmatizer()
ps = nltk.PorterStemmer()
            
def strip_accents(text):
    try:
        text = unicode(text, 'utf-8')
    except NameError: # unicode is a default on python 3 
        pass

    text = unicodedata.normalize('NFD', text)\
           .encode('ascii', 'ignore')\
           .decode("utf-8")
    return str(text)

def clean_up_sentence(text):
    
    # Shift to lowercase
    text = text.lower()
    
    # Removing mentions, hashtags and urls
    for i in range(len(text)):
        if text[i] == '#' or text[i] == '@':
            j = 0
            maxj = len(text)-i
            while(j <maxj and text[i+j] != ' '):
                if i+j < len(text):
                    text = text[0:i+j] + '.' + text[i+j+1:]
                    j += 1
        elif text[i] == 'h' and i < len(text)-4:
            if text[i:i+4] == 'http':
                j = 0
                maxj = len(text)-i
                while(j <maxj and text[i+j] != ' '):
                    if i+j < len(text):
                        text = text[0:i+j] + '#' + text[i+j+1:]
                        j += 1
    
    # Removing Punctuations and numbers
    text  = "".join([char for char in text if char not in string.punctuation])
    text = re.sub('[0-9]+', '', text)
    
    # Removing unwanted whitespace and removing accents
    text = strip_accents(" ".join(text.split()))
    
    # Tokenisation
    text = re.split('\W+', text)
    if '' in text:
        text.remove('')
       
    # Removing stop words
    text = [word for word in text if word not in stopword]
    
    # Lemmatization
    text = [wn.lemmatize(word) for word in text]

    # Remove Stopwords
    text = [word for word in text if word not in stopword]
    
    return text

# Loading all the models
reddit = pickle.load(open('Major_Project_Reddit.sav', 'rb'))
corona = pickle.load(open('Major_Project_Twitter_Corona.sav', 'rb'))
india = pickle.load(open('Major_Project_Twitter_India.sav', 'rb'))
mill = pickle.load(open('Major_Project_Twitter_1.6M.sav', 'rb'))
comb = pickle.load(open('Major_Project_Twitter_Combined.sav', 'rb'))

# Creating list of all models
models = [
        reddit,
        corona,
        india,
        mill,
        comb
    ]
    
# Providing names of all the models
model_names = [
        'Twitter Reddit',
        'Twitter Corona',
        'Twitter India',
        'Twitter 1.6 M Tweets',
        'All data Combined'
    ]

# Initialising the data needed for the voting
# (This data was achieved using the voting and evaluation of the previous models in one of the notebooks)
responses = ['Positive', 'Negative', 'Neutral']
resNums = [90767, 86082, 7659]
fscore = {'Twitter Reddit': {'Positive': 0.4827271811162671,
  'Negative': 0.2659666469190279,
  'Neutral': 0.11328732303996975},
 'Twitter Corona': {'Positive': 0.579134572809062,
  'Negative': 0.4487428698894236,
  'Neutral': 0.07083543705486148},
 'Twitter India': {'Positive': 0.5227219671620885,
  'Negative': 0.3432644047380044,
  'Neutral': 0.12461420441367992},
 'Twitter 1.6 M Tweets': {'Positive': 0.7622099609784753,
  'Negative': 0.7457948326904099,
  'Neutral': 0},
 'All data Combined': {'Positive': 0.7959466028493437,
  'Negative': 0.7776426006018942,
  'Neutral': 0.2078676150384671}}

def votePredict(ip):

  # Empty list to store the predictions of all models
  prd = []

  # Main predictor loop
  for i in range(len(models)):
      pl = models[i]
      pred = pl.predict([ip])
      prd.append(pred)

  # The voting system
  votes = [0 for res in responses]
    
  for j in range(len(prd)):
      for response in range(len(responses)):
          if responses[response] == prd[j]:
              votes[response] += fscore[model_names[j]][responses[response]]/resNums[response]**(3/5)
  max_index = 0
  max_list = []
  for vote in range(len(votes)):
      if votes[vote] > votes[max_index]:
          max_index = vote
          max_list = []
          max_list = [max_index,]
        
      elif votes[vote] == votes[max_index]:
          max_list.append(vote)
    
  return responses[random.choice(max_list)]

# --------------------------------------------------------------------
# Streamlit (Web app) Code
import streamlit as st

st.title('Classification using Sentiment Analysis')

st.write('This application is a simplistic way of suggesting the sentiment of any text. The application is capable of assigning:')
st.write('\t-Positive \U0001F60A')
st.write('\t-Neutral \U0001F610')
st.write('\t-Negative \U0001F614')
st.write('to a text provided to it.')
st.write('It has been made using ML model trained on data of millions of tweets and thousands of Reddit comments.')
st.write('\n\nFeel free to try out as many different things as you want. My sentiment towards that is Positive \U0001F60A')

ip = st.text_input('Enter text: ')

if len(ip) != 0:
  op = votePredict(ip)
  if op == 'Neutral':
    op += ' \U0001F610'
  elif op == 'Negative':
    op += ' \U0001F614'
  elif op == 'Positive':
    op += ' \U0001F60A'
  st.title(op)
