from flask import Flask, render_template, request, jsonify
from datetime import datetime
from openai import OpenAI
from duckduckgo_search import DDGS
import sys
import os

app = Flask(__name__)

try:
  client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
except KeyError:
  sys.stderr.write("""\nSet up OPENAI_API_KEY_REPLIT as a secret.\n""")
  sys.exit(1)

the_model = "gpt-3.5-turbo"

def ask_gpt(prompt):
    msg = [{"role": "user", "content": prompt}]
    chat_completion = client.chat.completions.create(model=the_model, messages=msg)
    reply = chat_completion.choices[0].message.content
    return reply

def ddgs(query):
    bodies=[]
    with DDGS() as ddgs:
        results = [r for r in ddgs.text(query, max_results=12)]
    for result in results:
        bodies.append(result["body"])
    return "\n".join(bodies)

@app.route('/', methods=['GET'])
def index():
    # No changes here; serves the main page
    return render_template('index.html')

@app.route('/get-time', methods=['POST'])
def get_time():
    # This route will handle the AJAX request and return the current time
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return jsonify({'time': current_time})


@app.route('/generate-message', methods=['POST'])
def generate_message():
    # Extracting the topic from the AJAX request.
    topic = request.json['topic']
    pre_message = "help me to write a 800 characters summary of the following news."
    pre_message = "关于以下的内容总结800字，不要提出其他帮助词汇："
    search_result_text = ddgs(topic)
    query = pre_message + "\n" + search_result_text
    trimmed_query = query[:4000] if len(query) > 400 else query
    print("GOT DDGS, sending to gpt now.")

    gpt_answer = ask_gpt(trimmed_query)
    generated_message = str(gpt_answer)
    return jsonify({'message': generated_message})

if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(host='0.0.0.0', debug=True)