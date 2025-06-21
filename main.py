import os
import sys
from dotenv import load_dotenv
from google import genai


def main():
    api_key = load_api_key()
    prompt = parse_arguments()

    client = genai.Client(api_key=api_key)
    response = generate_response(client, prompt)

    text = getattr(response, "text", None)
    prompt_token_count = getattr(response.usage_metadata, "prompt_token_count", None)
    candidates_token_count = getattr(
        response.usage_metadata, "candidates_token_count", None
    )

    print("\n--- Response ---")
    print(text or "[No response text received]")
    print("\n--- Usage Metadata ---")
    print(f"Prompt tokens: {prompt_token_count}")
    print(f"Response tokens: {candidates_token_count}")


def load_api_key():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY is not set in environment variables.")
        sys.exit(1)
    return api_key


def parse_arguments():
    if len(sys.argv) < 2:
        print("Usage: python3 main.py <prompt>")
        sys.exit(1)
    # Join all remaining arguments to support multi-word prompts
    prompt = " ".join(sys.argv[1:])
    return prompt


def generate_response(client, prompt):
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-001",
            contents=prompt,
        )
        return response
    except Exception as e:
        print(f"Error generating response: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
