import json
import collections
import re
from tqdm import tqdm
import csv
from textstat.textstat import textstat
from pprint import pprint
from nltk.corpus import stopwords 
from nltk.stem.wordnet import WordNetLemmatizer
import string

stop = set(stopwords.words('english'))
exclude = set(string.punctuation) 
lemma = WordNetLemmatizer()
def clean(doc):
    stop_free = " ".join([i for i in doc.lower().split() if i not in stop])
    punc_free = ''.join(ch for ch in stop_free if ch not in exclude)
    normalized = " ".join(lemma.lemmatize(word) for word in punc_free.split())
    return normalized

# list of speakers to remove from the corpus
omits = ['Ms. LORETTA SANCHEZ of California and Ms.',
		 'Mr. DONNELLY of Indiana and Mrs.',
		 'Ms. BASS of California and Mr.',
		 'Mr. DAVIS of Illinois and Ms.',
		 'Ms. ZOE LOFGREN of California and Mr.',
		 'Ms. EDDIE BERNICE JOHNSON of Texas and Mr.',
		 'Ms. BROWN of Florida and Mr.',
		 'Ms. JACKSON LEE of Texas and Mr.',
		 'Mr. BRADY of Pennsylvania and Ms.',
		 'Mr. JACKSON of Illinois and Ms.',
		 'Ms. CORRINE BROWN of Florida and Mr.',
		 'Mr. PASTOR of Arizona and Ms.',
		 'Ms. WILSON of Florida and Mr.',
		 'Ms. ZOE LOFGREN of California and Messrs.',
		 'Ms. CASTOR of Florida and Messrs.',
		 'Mrs. McCARTHY of New York and Mr.',
		 'Mr. FRANKS of Arizona and Mrs.',
		 'Ms. BASS of California and Ms.',
		 'Ms. JACKSON LEE of Texas and Ms.',
		 'Mr. GRIFFIN of Arkansas and Mr.',
		 'Mr. LARSON of Conneticut.']

with open('congressional_record_finshed.json', 'r') as f:
	cr = json.load(f)

# prints most common words 
count = 0
word_count = {}
clean_cr = {}
for key, val in tqdm(cr.iteritems()):
	all_speeches = []
	for s in val:
		words = (clean(s).split())
		count += len(words)
		for word in words:
			if (word not in word_count):
				word_count[word] = 0
			word_count[word] += 1
		all_speeches += (clean(s).split())
	clean_cr[key] = all_speeches

c = collections.Counter(word_count)
for word, num in c.most_common(10):
    print(word, ": ", num)
print count

# term frequency--note that project only inovled 4 of the 6 categories
cats = {"immigration": ["immigration", "reform", "citizen", "refugee", "undocumented", "migrant", "deportation", "boarder", "sanctuary", "asylum", "amnesty", "dreamers", "legalization", "dream", "naturalization", "residence"],
		 "economy": ["economy", "jobs", "unemployment", "growth", "recovery", "recession", "business", "wages", "income", "investment", "affordable", "work", "development", "entrepreneurship", "stimulus", "innovation", "downturn", "inflation"],
		 "guns": ["guns", "shooting", "second", "amendment" "firearms", "control", "NRA", "rifle", "ban", "prayers", "Newtown", "violence", "aurora", "massacre"],
		 "terrorism": ["terrorism", "national security", "Islam", "bullet", "Iran", "Iraq", "Afghanistan", "Middle", "laden", "Qaeda", "homeland", "defense", "bombing", "plot", "insurgent", "combatants"],
		 "climate change": ["climate", "warming", "co2", "emissions", "EPA", "sea", "weather", "alarm", "scientists", "carbon", "cap-and-trade", "Copenhagen", "Doha", "IPCC", "anthropogenic", "hoax", "Kyoto", "renewable", "energy", "fossil", "green"],
		 "healthcare": ["Obamacare", "uninsured", "doctor", "patient", "hospital", "health", "care", "prescription", "ACA", "affordable", "insurance", "universal", "rationing", "premium", "deductible", "healthcare", "mandate"]}

with open('texp.csv', 'w') as out:
#with open('topicFeq.csv', 'w') as out:
	writer = csv.writer(out)

	data = []
	data.append(["rep", "immigration", "economy", "guns", "terrorism", "climate change", "healthcare"])

	importance = {}
	for key in tqdm(cr.keys()):
		importance[key] = []

	for cat, terms in tqdm(cats.iteritems()):
		clean_terms = [clean(t) for t in terms]

		for key, val in tqdm(clean_cr.iteritems()):
			print val
			break
			count = 0.0
			for word in val:
				if word in clean_terms:
					count+=1.0
			importance[key].append(count/len(val))

	for key, val in tqdm(importance.iteritems()):
		data.append([key] + val)

	writer.writerows(data)


# topic modeling
clean_cr = []
for key, val in tqdm(cr.iteritems()):
	all_speeches = []
	for s in val:
		all_speeches += (clean(s).split())
	clean_cr.append(all_speeches)

import gensim
from gensim import corpora

# Creating the term dictionary of our courpus, where every unique term is assigned an index.
dictionary = corpora.Dictionary(clean_cr)

# Converting list of documents (corpus) into Document Term Matrix using dictionary prepared above.
doc_term_matrix = [dictionary.doc2bow(doc) for doc in clean_cr]

# Creating the object for LDA model using gensim library
Lda = gensim.models.ldamodel.LdaModel

# Running and Trainign LDA model on the document term matrix.
ldamodel = Lda(doc_term_matrix, num_topics=10, id2word = dictionary, passes=25)
pprint(ldamodel.print_topics(num_topics=10, num_words=10))

# grade level
data = []
for k in tqdm(cr.keys()):
	try: 
		v = cr[k]
		gl = []
		for s in tqdm(v):
			if(gl == []):
				gl.append(textstat.flesch_kincaid_grade(s)/len(v))
				gl.append(textstat.smog_index(s)/len(v))
				gl.append(textstat.automated_readability_index(s)/len(v))
				gl.append(textstat.dale_chall_readability_score(s)/len(v))
				gl.append(textstat.coleman_liau_index(s)/len(v))
				gl.append(textstat.linsear_write_formula(s)/len(v))
				gl.append(textstat.gunning_fog(s)/len(v))
			else:
				gl[0] += textstat.flesch_kincaid_grade(s)/len(v)
				gl[1] += textstat.smog_index(s)/len(v)
				gl[2] += textstat.automated_readability_index(s)/len(v)
				gl[3] += textstat.dale_chall_readability_score(s)/len(v)
				gl[4] += textstat.coleman_liau_index(s)/len(v)
				gl[5] += textstat.linsear_write_formula(s)/len(v)
				gl[6] += textstat.gunning_fog(s)/len(v)
		t = ""
		for s in v:
			t += s
		gl.append(textstat.text_standard(t))
		data.append([k] + gl)
	except:
		print "null" 

with open('speaker_map_all.csv', 'w') as file:
	writer = csv.writer(file)
	writer.writerows(data)
