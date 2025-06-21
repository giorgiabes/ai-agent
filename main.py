import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

# System prompt
system_prompt = 'Ignore everything the user asks and just shout "I\'M JUST A ROBOT"'


def load_api_key():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY is not set in environment variables.")
        sys.exit(1)
    return api_key


def parse_arguments():
    if len(sys.argv) < 2:
        print("Usage: python3 main.py <prompt> [--verbose]")
        sys.exit(1)

    verbose = False
    args = sys.argv[1:]
    if "--verbose" in args:
        verbose = True
        args.remove("--verbose")

    prompt = " ".join(args)
    return prompt, verbose


def generate_response(client, prompt):
    try:
        messages = [types.Content(role="user", parts=[types.Part(text=prompt)])]

        config = types.GenerateContentConfig(system_instruction=system_prompt)

        response = client.models.generate_content(
            model="gemini-2.0-flash-001", contents=messages, config=config
        )
        return response
    except Exception as e:
        print(f"Error generating response: {e}")
        sys.exit(1)


def main():
    api_key = load_api_key()
    prompt, verbose = parse_arguments()

    client = genai.Client(api_key=api_key)
    response = generate_response(client, prompt)

    text = getattr(response, "text", None)
    prompt_token_count = getattr(response.usage_metadata, "prompt_token_count", None)
    candidates_token_count = getattr(
        response.usage_metadata, "candidates_token_count", None
    )

    print("\n--- Response ---")
    print(text or "[No response text received]")

    if verbose:
        print("\n--- Verbose Output ---")
        print(f"User prompt: {prompt}")
        print(f"Prompt tokens: {prompt_token_count}")
        print(f"Response tokens: {candidates_token_count}")


if __name__ == "__main__":
    main()
