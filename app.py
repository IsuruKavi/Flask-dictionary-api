from flask import Flask, jsonify, request
import requests
import json
from translate import Translator

translator = Translator(to_lang="si")

app = Flask(__name__)

WORDS_API_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/"

def get_word_data(word):
    print(f"{WORDS_API_URL}{word}")
    response = requests.get(f"{WORDS_API_URL}{word}")
  
    if response.status_code != 200:
        return None
    return response.json()

@app.route('/word=<word>', methods=['GET'])
def get_meaning_of_word(word):
    word_data = get_word_data(word)
    try:
        data = word_data[0]['meanings']
        englishMeanings = []
        englishSimilarWord = []
        for i in data:
            dic1 = {}
            meaningsOfEachWord = []
            dic1['partOfSpeech'] = i['partOfSpeech']
            for j in i['definitions']:
                meaningsOfEachWord.append(j['definition'])
            englishSimilarWord += i["synonyms"]
            dic1['definitions'] = meaningsOfEachWord
            englishMeanings.append(dic1)
        englishMeanings.append({"similarWord": englishSimilarWord})
        print(englishMeanings[-1]['similarWord'])
        
        sinhala = translator.translate(englishMeanings[0]['definitions'][0])
        response_data = {
            "word": word,
            "english": englishMeanings,
            "sinhala": [{'meaning': translator.translate(word)}, {'definition': sinhala}]
        }
    except:
        return jsonify({
            "title": "No Definitions Found",
            "message": "Sorry pal, we couldn't find definitions for the word you were looking for.",
            "resolution": "You can try the search again at later time or head to the web instead."
        }), 404
        
    if word.isalpha():
        return jsonify(response_data), 200
    else:
        return jsonify({"error": "Enter the valid input"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)