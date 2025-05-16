from MLAgentBench.LLM import complete_text

def test_model():
    prompt = """You are a helpful AI programming expert. Please write a simple Python script that loads a CSV file and prints its first 5 rows.

Your response must start with ```python and end with ```. Do not include any other text or explanations."""

    try:
        response = complete_text(prompt, log_file="test.log")
        print("Model Response:")
        print(response)
        
        # Check if response has correct format
        if "```python" in response and "```" in response.split("```python", 1)[1]:
            code = response.split("```python", 1)[1].split("```", 1)[0].strip()
            print("\nExtracted Code:")
            print(code)
        else:
            print("\nError: Response does not contain properly formatted code block")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_model() 