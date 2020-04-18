import re
import urllib.request

from sklearn.base import BaseEstimator, TransformerMixin
import spacy
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords

STOP_WORD_ES = stopwords.words('spanish')
WORD_TOKENIZER = RegexpTokenizer("[\w']+")


nlp = spacy.load('es_core_news_sm')

LOGIT_BINARY_MODEL = "https://www.dropbox.com/s/l07e5geypwkcbyw/log_bin_pipeline.joblib?dl=1"

def downloader(url, path_file):
    with urllib.request.urlopen(url) as u:
        data = u.read()
    with open(path_file, "wb") as f :
        f.write(data)
    
def cleaner(speech):
    tt = speech.lower()
    tt = re.sub(r'\w*(@)\w*', '', tt)
    tt = re.sub(r'\w*(RT)\w*', '', tt, )
    tt = re.sub(r'\w*(#)\w*', '', tt, )
    tt = re.sub(r"\S*(\.com|\.ly|\.co|\.net|\.es|\.ar|\.uy|\.org|\.me|\.gl)\S*", "", tt)

    tt = re.sub(r'\w*(jaja|kaka|jeje|jiji|juju|jojo|ajaj|jaaj)\w*','jaja',tt)
#     tt = re.sub(r'[^\w\s]', '', tt)
    return tt

def tokenizer(document):
    return [token for token in WORD_TOKENIZER.tokenize(document) if token.isalpha()]

class Lematizator(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self
    
    def transform(self, X, y=None):
        if not isinstance(X, list):
            X = list(X)

        corpus_lema = []
        for doc in nlp.pipe(X, disable=["parser", "ner", 'textcat'], n_process=-1):
            corpus_lema.append(' '.join([ent.lemma_.lower() for ent in doc]))
        return corpus_lema
    
class Dataset():
    @staticmethod 
    def _remove_users(speech):
        return re.sub(r'\w*(@)\w*', '', speech)
    
    @staticmethod 
    def _remove_url(speech):
        return re.sub(r"\S*(\.com|\.ly|\.co|\.net|\.org|\.me|\.gl)\S*", "", speech)
    
    @staticmethod 
    def _remove_punctuation(speech):
        return re.sub(r'[^\w\s]', '', speech)
    
    @staticmethod 
    def _remove_hashtag(speech):
        return re.sub(r'\w*(#)\w*', '', speech)
    
    @staticmethod 
    def _reduce_laugh(speech):
        return re.sub(r'\w*(jaja|kaka|jeje|jiji|juju|jojo|ajaj|jaaj)\w*','jaja',speech)
    
    def _processed(self, speech):
        tt = speech.lower()
        tt = self._remove_users(tt)
        tt = self._remove_url(tt)
        tt = self._remove_hashtag(tt)
        tt = self._reduce_laugh(tt)
        tt = self._remove_punctuation(tt)
        tt = unidecode(tt)
        return tt
    
    def binary_class(self, dataset, processed=True):
        corpus = [self._processed(k['text']) if processed else k['text'] for k in dataset if k['klass'] != 'neutral']
        mapper = {'negative': 0, 'positive': 1}
        target = [mapper[k['klass']] for k in dataset if k['klass'] != 'neutral']
        
        return corpus, target
        

    def multi_class(self, dataset, processed=True):
        corpus = [self._processed(k['text']) if processed else k['text'] for k in dataset]
        mapper = {'neutral': 0, 'negative': -1, 'positive': 1}
        target = [mapper[k['klass']] for k in dataset]
        return corpus, target