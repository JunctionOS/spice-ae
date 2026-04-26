from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
import pandas as pd
import os
import re

cleanup_re = re.compile('[^a-z]+')
df_input = pd.DataFrame()
init_done = False
model = None
tfidf_vect = None

def cleanup(sentence):
    sentence = sentence.lower()
    sentence = cleanup_re.sub(' ', sentence).strip()
    return sentence

def function_handler(request_json):
    global init_done
    global model
    global tfidf_vect
    if not init_done:
        dataset_path = request_json['dataset_path']
        model_path = request_json['model_path']
        dataset = pd.read_csv(dataset_path)
        model = joblib.load(model_path)
        dataset['train'] = dataset['Text'].apply(cleanup)
        tfidf_vect = TfidfVectorizer(min_df=100).fit(dataset['train'])
        init_done = True
                
    prompt = request_json['prompt']
    df_input['x'] = [prompt]
    df_input['x'] = df_input['x'].apply(cleanup)
    processed = tfidf_vect.transform(df_input['x'])
    out = model.predict(processed)


