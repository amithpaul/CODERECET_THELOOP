import google.generativeai as genai
import json
import csv

# --- Configuration ---
try:
    # IMPORTANT: Replace "YOUR_API_KEY_HERE" with your actual API key.
    genai.configure(api_key="AIzaSyBVfuwhsmTb7MYRvN0-5Y8bMbAKh8vh9WM")
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    print(f"Error configuring API. Please check your key. Details: {e}")
    exit()

# --- Sample Innovations Data ---
innovations_data = [
    "We should create a mobile app to report potholes directly to the local panchayat. Users can upload a photo and the app will automatically get the GPS location. This would make our roads safer.",
    "I am very happy with the new public library's extended hours. It gives students like me a safe and quiet place to study for exams in the evening. Thank you for this wonderful initiative.",
    "The process to get a trade license for a new shop is incredibly slow and requires too many physical documents. It's very discouraging for young entrepreneurs trying to start a business.",
    "A project to install solar panels on all government school rooftops would be amazing. It would save electricity costs and also teach students about renewable energy."
]

def analyze_innovation(text: str) -> dict:
    """Analyzes text to generate a summary, tags, and sentiment."""
    print(f"Processing: '{text[:50]}...'")
    prompt = f"""
    Analyze the following innovation/suggestion. Your task is to extract three pieces of information:
    1.  A one-sentence summary of the core idea.
    2.  A list of 4 relevant topic tags (as a Python list of strings).
    3.  The overall sentiment (as "Positive", "Negative", or "Neutral").

    Return your analysis ONLY as a valid JSON object with the keys "summary", "tags", and "sentiment".

    Suggestion: "{text}"

    JSON Output:
    """
    try:
        response = model.generate_content(prompt)
        cleaned_json_string = response.text.strip().replace("```json", "").replace("```", "")
        analysis = json.loads(cleaned_json_string)
        return analysis
    except Exception as e:
        print(f"  -> Error analyzing text: {e}")
        return {"summary": "Error in analysis", "tags": [], "sentiment": "Unknown"}

# --- Main Program ---
if __name__ == "__main__":
    all_results = []
    for innovation in innovations_data:
        result = analyze_innovation(innovation)
        result['original_idea'] = innovation
        all_results.append(result)
        
    print("\n--- AI Analysis Complete ---")

    # Save results to a JSON file
    with open("innovations.json", 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print("✅ Results saved to innovations.json")

    # Save results to a CSV file
    headers = ['original_idea', 'summary', 'tags', 'sentiment']
    with open("innovations.csv", 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for row in all_results:
            row['tags'] = ', '.join(row.get('tags', []))
            writer.writerow(row)
    print("✅ Results saved to innovations.csv")