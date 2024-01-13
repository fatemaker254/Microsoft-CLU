from flask import Flask, render_template, request
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations import ConversationAnalysisClient
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)

# Replace these with your actual values
"""CLU_ENDPOINT = "https://emotiguard-clu.cognitiveservices.azure.com/"
CLU_KEY = "5881bff47ca340ebabc85378c1730ec8"
PROJECT_NAME = "EmotiGuardluis"
DEPLOYMENT_NAME = "EmotiGuard_CLU"""

CLU_ENDPOINT = os.getenv("CLU_ENDPOINT")
CLU_KEY = os.getenv("CLU_KEY")
PROJECT_NAME = os.getenv("PROJECT_NAME")
DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    if request.method == "POST":
        user_input = request.form["user_input"]

        # Analyze conversation using CLU
        client = ConversationAnalysisClient(CLU_ENDPOINT, AzureKeyCredential(CLU_KEY))
        with client:
            result = client.analyze_conversation(
                task={
                    "kind": "Conversation",
                    "analysisInput": {
                        "conversationItem": {
                            "participantId": "1",
                            "id": "1",
                            "modality": "text",
                            "language": "en",
                            "text": user_input,
                        },
                        "isLoggingEnabled": False,
                    },
                    "parameters": {
                        "projectName": PROJECT_NAME,
                        "deploymentName": DEPLOYMENT_NAME,
                        "verbose": True,
                    },
                }
            )

        # Extract relevant information from the CLU response
        top_intent = (
            result.get("result", {}).get("prediction", {}).get("topIntent", "N/A")
        )
        intent_category = (
            result.get("result", {})
            .get("prediction", {})
            .get("intents", [{}])[0]
            .get("category", "N/A")
        )
        confidence_score = (
            result.get("result", {})
            .get("prediction", {})
            .get("intents", [{}])[0]
            .get("confidenceScore", "N/A")
        )

        return render_template(
            "result.html",
            user_input=user_input,
            top_intent=top_intent,
            intent_category=intent_category,
            confidence_score=confidence_score,
        )


if __name__ == "__main__":
    app.run(debug=True)
