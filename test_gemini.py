
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

try:
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=(
            "Recommend one Korean romantic drama "
            "in two sentences."
        ),
    )

    print("\nGemini response:\n")
    print(response.text)

except Exception as error:
    print("\nGemini test failed:")
    print(error)