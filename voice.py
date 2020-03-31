from googletrans import Translator
def get_language_output(user_input):
	results =[]
	translator = Translator(service_urls=[
      'translate.google.com',
      'translate.google.co.kr',
    ])
	results.append(user_input)
	translations = translator.translate(results, dest='te')
	for translation in translations:
		return translation.text
