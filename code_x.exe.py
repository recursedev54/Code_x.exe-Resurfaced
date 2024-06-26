import os
import random
import spacy

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

def process_text(text):
    replacements = [
        ('"', ''), ("'", ''), ('\n', ' '), (')', ''), ('(', ''),
        ('[', ''), (']', ''), ('’', ''), ('“', ''), ('”', '')
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    return text.lower()

def read_files_from_folder(folder_path):
    corpus = ""
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            with open(os.path.join(folder_path, filename), 'r', encoding='utf-8') as file:
                corpus += process_text(file.read()) + " "
    return corpus

def build_ngram(corpus, n=4):
    ngram = {}
    words = corpus.split()
    for i in range(n, len(words)):
        key = tuple(words[i - n:i - 1])
        value = words[i - 1]
        if key not in ngram:
            ngram[key] = []
        ngram[key].append(value)
    return ngram

def weighted_choice(choices):
    total = sum(weight for choice, weight in choices)
    r = random.uniform(0, total)
    upto = 0
    for choice, weight in choices:
        if upto + weight >= r:
            return choice
        upto += weight

def generate_text(ngram, context_window, n=4):
    context = tuple(context_window[-(n-1):])
    if context not in ngram:
        context = random.choice(list(ngram.keys()))
    
    output = list(context)
    while True:
        if context not in ngram:
            break
        next_word_choices = ngram[context]
        next_word = weighted_choice([(word, next_word_choices.count(word)) for word in set(next_word_choices)])
        output.append(next_word)
        context = tuple(output[-(n-1):])
        if len(output) >= 100:  # Limit output length for practicality
            break
    return ' '.join(output)

class ChatbotState:
    def __init__(self):
        self.state = "initial"
        self.context_window = []

    def update_state(self, user_input):
        doc = nlp(user_input)
        if self.state == "initial":
            if any(token.lemma_ == "hello" for token in doc):
                self.state = "greeting"
        elif self.state == "greeting":
            self.state = "conversation"

    def generate_response(self, user_input, ngram):
        self.context_window.extend(user_input.split())
        response = generate_text(ngram, self.context_window)
        self.context_window.extend(response.split())
        return response

# Load and process corpus
folder_path = r"" #Here you Must put the local path to the codex transcripts I've made , check them out here https://github.com/zrebarchak/Codexchan.exe-Archive
corpus = read_files_from_folder(folder_path)

# Build 4-gram model
ngram = build_ngram(corpus)

# Initialize chatbot
chatbot = ChatbotState()

# Simulate conversation
user_input = "hello there"
chatbot.update_state(user_input)
response = chatbot.generate_response(user_input, ngram)
print("Bot:", response)

# Continue conversation
user_input = "how are you?"
chatbot.update_state(user_input)
response = chatbot.generate_response(user_input, ngram)
print("Bot:", response)
