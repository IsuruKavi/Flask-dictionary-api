from flask import Flask, jsonify, request
import requests
import pycountry
from translate import Translator
from database import collection

app = Flask(__name__)

WORDS_API_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/"

def get_word_data(word):
    # Function to fetch word data from the API
    response = requests.get(f"{WORDS_API_URL}{word}")
    if response.status_code != 200:
        return None
    return response.json()

def get_language_code(language_name):
    # Function to get the language code from the language name
    try:
        language = pycountry.languages.lookup(language_name)
        return language.alpha_2 if hasattr(language, 'alpha_2') else language.alpha_3
    except LookupError:
        return None

def translate_first_definition(definition, language_code):
    # Function to translate the first definition to the specified language
    translator = Translator(to_lang=language_code)
    translated_definition = translator.translate(definition)
    return translated_definition

@app.route('/translate', methods=['GET'])
def get_meaning_of_word():
    # Endpoint to get the meaning of a word in a specified language
    word = request.args.get('word')
    language = request.args.get('language')
    
    if not (word and language):
        return jsonify({'error': 'Missing required query parameters'}), 400
    
    # Check if the word is already in the database
    word_document = collection.find_one({"word": word})
    if word_document:
        print("Found in database")
        english_meanings = word_document['english_meanings']
    else:
        print("Not found in database")
        language_code = get_language_code(language)
        if not language_code:
            return jsonify({'error': f'Language "{language}" is not recognized'}), 400

        word_data = get_word_data(word)
        if not word_data:
            return jsonify({
                "title": "No Definitions Found",
                "message": "Sorry, we couldn't find definitions for the word you were looking for.",
                "resolution": "You can try the search again later or head to the web instead."
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
            
            # Translate the first definition
            translated_definition = translate_first_definition(definitions[0], language_code)
            
            # Insert data into MongoDB
            data_to_database = {"word": word, "english_meanings": english_meanings}
            collection.insert_one(data_to_database)
            
            response_data = {
                "word": word,
                "english": english_meanings,
                "secondaryLanguage": {
                    "info": [
                        {'meaning': word},  # Translator.translate(word) removed as it translates the word itself, not its meaning
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

    # If the word is found in the database, translate its meanings
    try:
        if 'english_meanings' in word_document:
            english_meanings = word_document['english_meanings']
        else:
            return jsonify({"error": "English meanings not found for the word"}), 404
        
        language_code = get_language_code(language)
        if not language_code:
            return jsonify({'error': f'Language "{language}" is not recognized'}), 400
        
        # Translate the first definition
        translated_definition = translate_first_definition(english_meanings[0]['definitions'][0], language_code)
        
        response_data = {
            "word": word,
            "english": english_meanings,
            "secondaryLanguage": {
                "info": [
                    {'meaning': word},  # Translator.translate(word) removed as it translates the word itself, not its meaning
                    {'definition': translated_definition}
                ],
                "LanguageIsoCode": language_code,
                "language": language
            }
        }
        return jsonify(response_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
