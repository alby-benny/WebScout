import google.generativeai as genai

def summarization(user_query, query_result):
  genai.configure(api_key = "API_KEY")

  model=genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  system_instruction="Act like a chat bot and the response to the query should be precise try to give answer in maximum 3 to 4 sentences")

  response = model.generate_content(f"Based on the {user_query} extract the result from the given data don't remove keywords:{query_result}",
        generation_config = genai.GenerationConfig(
        max_output_tokens=200,
        temperature=0.1,
    ))

  return response.text