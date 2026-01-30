import os
import sys
import json
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env files (script directory takes precedence over project root)
script_dir = Path(__file__).parent
load_dotenv(dotenv_path=script_dir / ".env")  # .claude/skills/process/scripts/.env
load_dotenv()  # Project root .env

# Provider defaults
DEFAULT_MODELS = {
    "gemini": "gemini-3-flash-preview",
    "anthropic": "claude-sonnet-4-5-20250929",
}


def get_config():
    """Reads LLM configuration from environment variables."""
    provider = os.getenv("LLM_PROVIDER", "anthropic").lower()
    model = os.getenv("LLM_MODEL", DEFAULT_MODELS.get(provider, ""))
    api_key = os.getenv("LLM_API_KEY")

    # Backward compatibility: fallback to provider-specific key
    if not api_key:
        fallback_keys = {
            "gemini": "GEMINI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
        }
        fallback = fallback_keys.get(provider)
        if fallback:
            api_key = os.getenv(fallback)

    if not api_key:
        raise Exception(
            f"No API key found. Set LLM_API_KEY or the provider-specific key for '{provider}'."
        )

    return provider, model, api_key


def call_gemini(prompt, model, api_key, temperature, response_type):
    from google import genai
    from google.genai import types

    client = genai.Client(
        api_key=api_key, http_options=types.HttpOptions(timeout=30000)
    )

    config_kwargs = {"temperature": temperature}
    if response_type == "json":
        config_kwargs["response_mime_type"] = "application/json"

    response = client.models.generate_content(
        model=model,
        contents=[prompt],
        config=types.GenerateContentConfig(**config_kwargs),
    )
    return response.text


def call_anthropic(prompt, model, api_key, temperature, response_type):
    import anthropic

    client = anthropic.Anthropic(api_key=api_key, timeout=60.0)

    system = None
    if response_type == "json":
        system = (
            "You must respond with valid JSON only. "
            "Do NOT wrap your response in markdown code fences (```json or ```). "
            "Do NOT include any explanatory text before or after the JSON. "
            "Your entire response must be parseable as JSON."
        )

    kwargs = {
        "model": model,
        "max_tokens": 8192,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
    }
    if system:
        kwargs["system"] = system

    response = client.messages.create(**kwargs)
    return response.content[0].text


PROVIDERS = {
    "gemini": call_gemini,
    "anthropic": call_anthropic,
}


def validate_and_clean_response(response, response_type):
    """
    Validates and cleans the response based on the expected type.
    For JSON: removes markdown code fences and validates JSON structure.
    For text: returns as-is.
    """
    if response_type == "text":
        return response

    if response_type == "json":
        # Remove markdown code fences if present
        cleaned = response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        # Validate JSON
        try:
            json.loads(cleaned)
            return cleaned
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response: {e}")

    return response


def main():
    parser = argparse.ArgumentParser(description="Send a prompt to an LLM.")
    parser.add_argument(
        "--prompt-file", required=True, help="Path to the prompt file."
    )
    parser.add_argument(
        "--output-file", required=True, help="Path to write the LLM response."
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.2,
        help="Sampling temperature (default: 0.2).",
    )
    parser.add_argument(
        "--response-type",
        choices=["text", "json"],
        default="text",
        help="Expected response format: text (default) or json.",
    )
    args = parser.parse_args()

    try:
        provider, model, api_key = get_config()

        if provider not in PROVIDERS:
            raise Exception(
                f"Unsupported provider: '{provider}'. Supported: {', '.join(PROVIDERS.keys())}"
            )

        print(f"Provider: {provider}, Model: {model}", file=sys.stderr)

        with open(args.prompt_file, "r", encoding="utf-8") as f:
            prompt = f.read()

        if not prompt.strip():
            raise Exception("Prompt file is empty.")

        print(f"Sending prompt ({len(prompt)} chars)...", file=sys.stderr)

        call_fn = PROVIDERS[provider]
        response = call_fn(prompt, model, api_key, args.temperature, args.response_type)

        # Validate and clean response based on expected type
        try:
            cleaned_response = validate_and_clean_response(response, args.response_type)
        except ValueError as e:
            print(f"\n[!] Response validation failed: {e}", file=sys.stderr)
            print(f"Raw response preview: {response[:500]}...", file=sys.stderr)
            sys.exit(1)

        with open(args.output_file, "w", encoding="utf-8") as f:
            f.write(cleaned_response)

        print(f"Response written to {args.output_file}", file=sys.stderr)

    except FileNotFoundError as e:
        print(f"\n[!] File not found: {e}", file=sys.stderr)
        sys.exit(1)
    except ConnectionError as e:
        print(f"\n[!] Connection error: {e}", file=sys.stderr)
        print(f"Provider: {provider}, Model: {model}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n[!] LLM call failed.", file=sys.stderr)
        print(f"Cause: {e}", file=sys.stderr)
        print(f"Provider: {provider}, Model: {model}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
