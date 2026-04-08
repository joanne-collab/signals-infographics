import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from bs4 import BeautifulSoup

def project_manager(data, template_path="index.html", output_file="final_infographic.html"):
    """
    Project Manager: Injects JSON data into index.html placeholders
    using BeautifulSoup and saves as final_infographic.html.
    """
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")

        # Inject Title and Subtitle
        title_full = data.get("title", ": ")
        if ": " in title_full:
            title, subtitle = title_full.split(": ", 1)
        else:
            title, subtitle = title_full, ""
        
        soup.find(id="edition-title").string = title
        soup.find(id="edition-subtitle").string = subtitle

        # Inject Modular Blocks
        infographic_content = soup.find(id="infographic-content")
        infographic_content.clear()

        for block in data.get("content_blocks", []):
            b_type = block.get("type")
            
            if b_type == "metrics":
                wrapper = soup.new_tag("div", **{"class": "grid grid-cols-1 md:grid-cols-2 gap-6"})
                h2 = soup.new_tag("h2", **{"class": "text-2xl font-bold col-span-full"})
                h2.string = block.get("title", "")
                wrapper.append(h2)
                for item in block.get("items", []):
                    item_div = soup.new_tag("div", **{"class": "bg-slate-50 p-6 rounded-xl"})
                    val = soup.new_tag("div", **{"class": "text-3xl font-bold text-[var(--brand-primary)]"})
                    val.string = item.get("value", "")
                    label = soup.new_tag("div", **{"class": "text-sm text-slate-600"})
                    label.string = item.get("label", "")
                    item_div.append(val)
                    item_div.append(label)
                    wrapper.append(item_div)
                infographic_content.append(wrapper)

            elif b_type == "sequence":
                wrapper = soup.new_tag("div", **{"class": "space-y-6"})
                h2 = soup.new_tag("h2", **{"class": "text-2xl font-bold"})
                h2.string = block.get("title", "")
                wrapper.append(h2)
                for step in block.get("steps", []):
                    step_div = soup.new_tag("div", **{"class": "border-l-4 border-[var(--brand-primary)] pl-6 py-2"})
                    step_p = soup.new_tag("p", **{"class": "font-medium"})
                    step_p.string = step
                    step_div.append(step_p)
                    wrapper.append(step_div)
                infographic_content.append(wrapper)

            elif b_type == "insights":
                wrapper = soup.new_tag("div", **{"class": "bg-[var(--brand-light)] p-8 rounded-2xl"})
                h2 = soup.new_tag("h2", **{"class": "text-2xl font-bold mb-4"})
                h2.string = block.get("title", "")
                wrapper.append(h2)
                for point in block.get("points", []):
                    p = soup.new_tag("p", **{"class": "mb-3 italic"})
                    p.string = f"• {point}"
                    wrapper.append(p)
                infographic_content.append(wrapper)

            elif b_type == "comparison":
                wrapper = soup.new_tag("div", **{"class": "grid grid-cols-2 gap-4"})
                h2 = soup.new_tag("h2", **{"class": "text-2xl font-bold col-span-full"})
                h2.string = block.get("title", "")
                wrapper.append(h2)
                
                # Headers
                a_header = soup.new_tag("div", **{"class": "font-bold text-center border-b pb-2"})
                a_header.string = block.get("side_a_name")
                wrapper.append(a_header)
                b_header = soup.new_tag("div", **{"class": "font-bold text-center border-b pb-2"})
                b_header.string = block.get("side_b_name")
                wrapper.append(b_header)
                
                for item in block.get("items", []):
                    a = soup.new_tag("div", **{"class": "p-2 text-sm"})
                    a.string = item.get("a", "")
                    b = soup.new_tag("div", **{"class": "p-2 text-sm"})
                    b.string = item.get("b", "")
                    wrapper.append(a)
                    wrapper.append(b)
                infographic_content.append(wrapper)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(str(soup))
        print(f"Final infographic saved to {output_file}")

    except Exception as e:
        print(f"Error in Project Manager: {e}")

def summarize_research(file_path="research.txt", output_file="data.json"):
    """
    Reads a research text file, summarizes it using the Gemini API,
    and saves the result as a JSON file.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            research_text = f.read()
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return

    # Configure the Gemini API
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        print("Error: GEMINI_API_KEY environment variable not set.")
        return
    genai.configure(api_key=gemini_api_key)

    # Initialize the Generative Model
    model = genai.GenerativeModel("gemini-flash-latest")

    # Craft the prompt for summarization and JSON formatting
    # Using double braces for f-string literal curly braces
    prompt = (f"Analyze the following research text and return a JSON object with a 'title' (a catchy title) and a list of 'content_blocks'. "
              f"Choose 2 to 3 content blocks from these allowed types:\n"
              f"- metrics: (title, items: [{{ 'value': '...', 'label': '...' }}])\n"
              f"- sequence: (title, steps: ['...'])\n"
              f"- insights: (title, points: ['...'])\n"
              f"- comparison: (title, side_a_name: '...', side_b_name: '...', items: [{{ 'a': '...', 'b': '...' }}])\n"
              f"Ensure the output is strictly valid JSON.\n\nResearch Text:\n{research_text}\n\nJSON Output:")

    try:
        response = model.generate_content(prompt)
        # Handle cases where the model might wrap JSON in markdown code blocks
        text_content = response.text.strip()
        if text_content.startswith("```json"):
            text_content = text_content[7:]
        if text_content.endswith("```"):
            text_content = text_content[:-3]
        text_content = text_content.strip()

        summary_json = json.loads(text_content)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(summary_json, f, indent=4)
        print(f"Summary successfully saved to {output_file}")
        
        # Inject branding and data into the template
        project_manager(summary_json)

    except Exception as e:
        print(f"An error occurred during Gemini API call or JSON processing: {e}")

if __name__ == "__main__":
    summarize_research()
