# from gevent import monkey
# monkey.patch_all()
import json
import os
import re
from pprint import pprint

import openai
from dotenv import load_dotenv
from dropbox_sign import ApiClient, ApiException, Configuration, apis, models
from flask import Flask, jsonify, request
from flask_cors import CORS

load_dotenv()
app = Flask(__name__)
CORS(app)


# OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")


@app.route("/api/summarize", methods=["POST"])
def summarize():
    try:
        data = request.get_json()
        transcript = data.get("transcript", "")
        cleaned_transcript = preprocess_transcript(transcript)

        # summary using GPT-3
        generated_summary = generate_summary(cleaned_transcript)
        print("Generated Summary:", generated_summary) 

        legal_document = generate_legal_document(generated_summary)
        print("Generated Legal Document:", legal_document) 

        return jsonify({"summary": generated_summary, "legal_document": legal_document})
        # response = openai.ChatCompletion.create(
        #     model="gpt-3.5-turbo-16k",
        #     messages=[{"role": "user", "content" : generated_summary}],
        #     max_tokens=4000,
        #     n=1,
        #     stop=None,
        # )
        # print("Generated Response:", response['choices'][0]['message']['content'].strip()) 

        # # generated_responses = [choice.text.strip() for choice in response.choices]
        # generated_responses = response['choices'][0]['message']['content'].strip()

        # return jsonify({"summary": generated_summary, "responses": generated_responses})

    except Exception as e:
        return jsonify({"error": str(e)})

#dropbox
configuration = Configuration(
    username = os.getenv("DROPBOX_API_KEY"),
)


# with ApiClient(configuration) as api_client:
#             signature_request_api = apis.SignatureRequestApi(api_client)

#             signer_1 = models.SubSignatureRequestSigner(
#                 email_address="thydoraemon13@gmail.com",
#                 name="Thy",
#                 order=0,
#             )

#             signer_2 = models.SubSignatureRequestSigner(
#                 email_address="0509biancafu@gmail.com",
#                 name="Bianca",
#                 order=1,
#             )

#             signing_options = models.SubSigningOptions(
#                 draw=True,
#                 type=True,
#                 upload=True,
#                 phone=True,
#                 default_type="draw",
#             )

#             data = models.SignatureRequestCreateEmbeddedRequest(
#                 client_id=os.getenv("CLIENT_ID"),
#                 title="NDA with Acme Co.",
#                 subject="The NDA we talked about",
#                 message="Please sign this NDA and then we can discuss more. Let me know if you have any questions.",
#                 signers=[signer_1, signer_2],
#                 cc_email_addresses=["thy_doraemon@yahoo.com"],
#                 files=[open("legal_document.pdf", "rb")],
#                 signing_options=signing_options,
#                 test_mode=True,
#             )

#             try:
#                 response = signature_request_api.signature_request_create_embedded(data)
#                 pprint(response)
#             except ApiException as e:
#                 print("Exception when calling Dropbox Sign API: %s\n" % e)

# with ApiClient(configuration) as api_client:
#     embedded_api = apis.EmbeddedApi(api_client)

#     signature_id = "a2d0723f7b75d5449210d36b2656e4a0"

#     try:
#         response = embedded_api.embedded_sign_url(signature_id)
#         pprint(response)
#     except ApiException as e:
#         print("Exception when calling Dropbox Sign API: %s\n" % e)

#embedded sign
def embeddedSign(signid):
    with ApiClient(configuration) as api_client:
        embedded_api = apis.EmbeddedApi(api_client)

        signature_id = signid

        try:
            response = embedded_api.embedded_sign_url(signature_id)
            pprint(response)
            print('CHECK RES', response["embedded"]["sign_url"])
            return response["embedded"]["sign_url"]

        except ApiException as e:
            print("Exception when calling Dropbox Sign API: %s\n" % e)
                
@app.route("/api/dropbox", methods=["GET", "POST"])
#embedded
def dropbox():
    try:
        #get signature id
        with ApiClient(configuration) as api_client:
            signature_request_api = apis.SignatureRequestApi(api_client)

            signer_1 = models.SubSignatureRequestSigner(
                email_address="thydoraemon13@gmail.com",
                name="Thy",
                order=0,
            )

            # signer_2 = models.SubSignatureRequestSigner(
            #     email_address="0509biancafu@gmail.com",
            #     name="Bianca",
            #     order=1,
            # )

            signing_options = models.SubSigningOptions(
                draw=True,
                type=True,
                upload=True,
                phone=True,
                default_type="draw",
            )

            data = models.SignatureRequestCreateEmbeddedRequest(
                client_id=os.getenv("CLIENT_ID"),
                title="NDA with Acme Co.",
                subject="The NDA we talked about",
                message="Please sign this NDA and then we can discuss more. Let me know if you have any questions.",
                signers=[signer_1],
                cc_email_addresses=["thy_doraemon@yahoo.com"],
                files=[open("legal_document.pdf", "rb")],
                signing_options=signing_options,
                test_mode=True,
            )

            try:
                response = signature_request_api.signature_request_create_embedded(data)
                pprint(response)
                #calling embeddedSign
                print(response)
                for object in response["signature_request"]["signatures"]:
                    print("embedded signature id", object["signature_id"])
                    url = embeddedSign(object["signature_id"])

                return jsonify({"sign_url": url})
                


            except ApiException as e:
                print("Exception when calling Dropbox Sign API: %s\n" % e)


    except Exception as e:
        return jsonify({"error": str(e)})


def preprocess_transcript(transcript):
    cleaned_transcript = re.sub(r'\d{2}:\d{2}:\d{2}:', '. ', transcript)
    sentences = re.split(r'(?<=[.!?])\s+', cleaned_transcript)
    cleaned_sentences = [s.strip() for s in sentences if len(s) > 10]
    return '. '.join(cleaned_sentences)

def generate_summary(text):
    # Sending the text to OpenAI's GPT-3.5 Turbo API
    try:
        # Ensure that text length does not exceed the maximum token limit for the model
        if len(text.split()) > 4096:  # Splitting by whitespace for simplicity
            raise ValueError("Text exceeds the maximum token limit for GPT-3.5 Turbo.")
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant that summarizes text."},
            {"role": "user", "content": f"Summarize: {text}"}
        ]
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=messages,
            max_tokens=4000,  # Adjust max_tokens as per your requirement
            temperature=0.7  # Adjust temperature as per your requirement
        )

        
        summary = response['choices'][0]['message']['content'].strip()
        return summary
    
    except Exception as e:
        print(f"Error in generating summary: {str(e)}")
        return ""
def generate_legal_document(summary):
    try:
        messages = [
            {
                "role": "system",
                "content": ("You are a helpful assistant that generates legal documents "
                            "based on provided summaries and key points. Ensure the generated document "
                            "is coherent, uses formal and professional language, and adheres to general "
                            "legal standards. Create a document that aligns closely with the mentioned "
                            "details and specifications in the summary.")
            },
            {
                "role": "user",
                "content": f"Create a legal document based on the following summary: {summary}"
            }
        ]
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=messages,
            max_tokens=4000,  # Adjust max_tokens as per your requirement
            temperature=0.7  # Adjust temperature as per your requirement
        )
        
        legal_document = response['choices'][0]['message']['content'].strip()
        return legal_document
    
    except Exception as e:
        print(f"Error in generating legal document: {str(e)}")
        return ""

if __name__ == "__main__":
    app.run(debug=True, threaded=True, host='0.0.0.0', port=8080)
