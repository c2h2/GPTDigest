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

the_model = "gpt-3.5-turbo-0125"

def ask_gpt(prompt):
    msg = [{"role": "user", "content": prompt}]
    chat_completion = client.chat.completions.create(model=the_model, messages=msg)
    reply = chat_completion.choices[0].message.content
    return reply

def ddgs(query):
    #bodies = []
    with DDGS() as ddgs:
        results = [r for r in ddgs.text(query, max_results=20)]
    #for result in results:
    #    bodies.append(result["body"])
    #return "\n".join(bodies)
    return results

@app.route('/')
def index():
    # No changes here; serves the main page
    return "Hello World!"

@app.route('/chat', methods=['GET'])
def chat():
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
    #pre_message = "help me to write a 1000 words summary of the following news snippts."
    pre_message = "关于以下的内容总结1000字，不要提出其他帮助词汇："
    search_results = ddgs(topic)
    search_result_text = "\n".join([result["body"] for result in search_results])
    query = pre_message + "\n" + search_result_text
    trimmed_query = query[:8000] if len(query) > 8000 else query
    print("GOT DDGS, sending to gpt now.")

    gpt_answer = ask_gpt(trimmed_query)
    generated_message = str(gpt_answer)
    #append a log file, log the query and the response
    fn = "/var/log/gptdigst_query.log"
    f=open(fn, "a")
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    f.write(f"{current_time} | Query: " + query + "\n")
    f.write(f"{current_time} | Search Result: " + str(search_results) + "\n")
    f.write(f"{current_time} | Response: " + generated_message + "\n")
    
    return jsonify({'message': generated_message})

if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(host='0.0.0.0', debug=True)