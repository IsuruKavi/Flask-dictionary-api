from flask import Flask, jsonify, request
import requests
import pycountry
from translate import Translator

app = Flask(__name__)

WORDS_API_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/"

def get_word_data(word):
    response = requests.get(f"{WORDS_API_URL}{word}")
    if response.status_code != 200:
        return None
    return response.json()

def get_language_code(language_name):
    try:
        language = pycountry.languages.lookup(language_name)
        return language.alpha_2 if hasattr(language, 'alpha_2') else language.alpha_3
    except LookupError:
        return None

@app.route('/translate', methods=['GET'])
def get_meaning_of_word():
    word = request.args.get('word')
    language = request.args.get('language')
    
    if not (word and language):
        return jsonify({'error': 'Missing required query parameters'}), 400
    
    language_code = get_language_code(language)
    if not language_code:
        return jsonify({'error': f'Language "{language}" is not recognized'}), 400

    translator = Translator(to_lang=language_code)
    word_data = get_word_data(word)
    if not word_data:
        return jsonify({
            "title": "No Definitions Found",
            "message": "Sorry pal, we couldn't find definitions for the word you were looking for.",
            "resolution": "You can try the search again at later time or head to the web instead."
        }), 404

    try:
        data = word_data[0]['meanings']
        english_meanings = []
        english_similar_words = []
        for meaning in data:
            part_of_speech = meaning['partOfSpeech']
            definitions = [definition['definition'] for definition in meaning['definitions']]
            synonyms = meaning.get('synonyms', [])
            english_meanings.append({'partOfSpeech': part_of_speech, 'definitions': definitions})
            english_similar_words.extend(synonyms)

        english_meanings.append({"similarWords": english_similar_words})
        
        translated_definition = translator.translate(english_meanings[0]['definitions'][0])
        response_data = {
            "word": word,
            "english": english_meanings,
            "secondaryLanguage": {
                "info": [
                    {'meaning': translator.translate(word)}, 
                    {'definition': translated_definition}
                ],
                "LanguageIsoCode": language_code,
                "language": language
            }
        }
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    if word.isalpha():
        return jsonify(response_data), 200
    else:
        return jsonify({"error": "Enter a valid word"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
