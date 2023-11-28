from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_restx import Api, Resource, fields
import unicodedata
from googletrans import Translator

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
api = Api(app, version='1.0', title='Translation API',
          description='A simple Translation API')
translator = Translator()

ns = api.namespace('translate', description='Translation operations')

translation_model = api.model('TranslationInput', {
    'input_text': fields.String(required=True, description='Text to translate'),
    'dest': fields.String(description='Destination language (default: en)')
})

def remove_diacritics(text):
    if text is None:
        return ''
    normalized_text = unicodedata.normalize('NFD', text)
    return ''.join(char for char in normalized_text if unicodedata.category(char) != 'Mn')

@ns.route('/')
class Translate(Resource):
    @ns.doc('translate_text')
    @ns.expect(translation_model, validate=True)
    def post(self):
        input_data = request.json
        input_text = input_data['input_text']
        dest = input_data.get('dest', 'en')

        try:
            translated_text = translator.translate(input_text, dest=dest).text
            detected_lang = translator.detect(input_text).lang
            pronunciation = translator.translate(input_text, dest=dest).pronunciation
            pronunciation = remove_diacritics(pronunciation)

            return {
                "translated_text": translated_text, 
                "pronunciation": pronunciation, 
                "detected_language": detected_lang
            }
        except Exception as e:
            return {"error": str(e)}, 500

@app.route("/")
def hello_world():
    return "Hello, World! This is a simple Flask API for translation."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
