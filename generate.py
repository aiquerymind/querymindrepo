# import anthropic  # Removed for Gemini-only deployment

num_prompt_tokens = len(enc.encode(f"Human: {prompt} Assistant: ")) 