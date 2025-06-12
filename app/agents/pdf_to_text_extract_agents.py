from app.services._get_prediction import get_prediction
from app.services.pdf_to_text import create_pdf_to_text_prediction

def pdf_to_text_extract(pdf_url):
    try :
        # Create a PDF to text prediction
        prediction_id = create_pdf_to_text_prediction(pdf_url)
        # Get the text from the prediction
        result = get_prediction(prediction_id)
        print(result['output'])
        return result['output']
    except Exception as e:
        print(f"Error: {e}")
        