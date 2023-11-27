from fastapi import FastAPI, HTTPException
from starlette.middleware.cors import CORSMiddleware as CORSMiddleware  # noqa
from googletrans import Translator
import unicodedata
from pydantic import BaseModel
from mangum import Mangum

app = FastAPI()
translator = Translator()
handler = Mangum(app)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
)

class TranslationInput(BaseModel):
    input_text: str

def remove_diacritics(text):
    if text is None:
        return ''
    normalized_text = unicodedata.normalize('NFD', text)
    return ''.join(char for char in normalized_text if unicodedata.category(char) != 'Mn')

@app.post("/translate/")
async def translate_text(input_data: TranslationInput, dest: str = 'en'):
    input_text = input_data.input_text
    try:
        translated_text = translator.translate(input_text, dest=dest).text
        detected_lang = translator.detect(input_text).lang
        print(translator.translate(input_text, dest=dest).pronunciation)
        
        pronunciation = translator.translate(input_text, dest=dest).pronunciation
        pronunciation = remove_diacritics(pronunciation)

        print("detected_lang: ", detected_lang)
        print("translated_text: ", translated_text)
        return {"translated_text": translated_text, "pronunciation": pronunciation, "detected_language": detected_lang}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)