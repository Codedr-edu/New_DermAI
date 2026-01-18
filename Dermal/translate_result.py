#from googletrans import Translator
#translator = Translator()
from deep_translator import GoogleTranslator
def translate_result(result):
    for r in result:
        r['class'] = translator.translate(r['class'], src='vi', dest='en').text
    return result

def translate(text):
    return GoogleTranslator(src='vi', dest='en').translate(text)
