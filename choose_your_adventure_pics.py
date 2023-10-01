import tkinter as tk
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from langchain.memory import CassandraChatMessageHistory, ConversationBufferMemory
from langchain.llms import OpenAI
from langchain import LLMChain, PromptTemplate
import json
from diffusers import StableDiffusionPipeline
import torch
from PIL import Image
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler

cloud_config= {
  'secure_connect_bundle': 'secure-connect-choose-your-adventure.zip'
}

with open("choose_your_adventure-token.json") as f:
    secrets = json.load(f)

CLIENT_ID = secrets["clientId"]
CLIENT_SECRET = secrets["secret"]
ASTRA_DB_KEYSPACE = "database"
OPENAI_API_KEY = ""

auth_provider = PlainTextAuthProvider(CLIENT_ID, CLIENT_SECRET)
cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
session = cluster.connect()

message_history = CassandraChatMessageHistory(
    session_id="anything",
    session=session,
    keyspace=ASTRA_DB_KEYSPACE,
    ttl_seconds=3600
)

message_history.clear()

cass_buff_memory = ConversationBufferMemory(
    memory_key="chat_history",
    chat_memory=message_history
)

template = """
You are now the guide of a mystical journey in the Whispering Woods. 
A traveler named Pelicanu seeks the lost Gem of Serenity. 
You must navigate her through challenges, choices, and consequences, 
dynamically adapting the tale based on the traveler's decisions. 
Your goal is to create a branching narrative experience where each choice 
leads to a new path, ultimately determining Pelicanu's fate. 

Here are some rules to follow:
1. Start by asking the player to choose some kind of weapons that will be used later in the game
2. Have a few paths that lead to success
3. Have some paths that lead to death. If the user dies generate a response that explains the death and ends in the text: "The End.", I will search for this text to end the game

Here is the chat history, use this to understand what to say next: {chat_history}
Human: {human_input}
AI:"""

prompt = PromptTemplate(
    input_variables=["chat_history", "human_input"],
    template=template
)

llm = OpenAI(openai_api_key=OPENAI_API_KEY)
llm_chain = LLMChain(
    llm=llm,
    prompt=prompt,
    memory=cass_buff_memory
)

def send_message():
        user_input = entry.get()
        if not chat_history.get("1.0", "end-1c"):
            chat_history.insert(tk.END, "Welcome to Choose Your Adventure Chatbot!\n")
        response = llm_chain.predict(human_input=user_input)
        meaning = f'In three words what is the meaning of {response} and {user_input}'
        chat_history.insert(tk.END, f"\nYou: {user_input}")
        chat_history.insert(tk.END, f"\nAI: {response.strip()}")
        entry.delete(0, tk.END)

        model_id = "stabilityai/stable-diffusion-2-1"

        # Use the DPMSolverMultistepScheduler (DPM-Solver++) scheduler here instead
        pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
        pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
        pipe = pipe.to("cuda")



        # Create an instance of the pyttsx3 engine
      # engine = pyttsx3.init()

        # Set the voice rate
      #  engine.setProperty('rate', 125)

        # Set the volume
      #  engine.setProperty('volume', 1.0)

        # Set the voice
      #  voices = engine.getProperty('voices')
      #  engine.setProperty('voice', voices[0].id)

        # Convert text to speech
       # engine.say(response)

        # Run the engine and convert the text to speech
       # engine.runAndWait()

        prompt = meaning
        image = pipe(prompt).images[0]
        image.save("generated_image.png")
        generated_image = Image.open("generated_image.png")

        # Display the image
        generated_image.show()
        print("Image saved!")

        if "The End." in response:
            entry.config(state=tk.DISABLED)
        return response
root = tk.Tk()
root.title("Choose Your Adventure Chatbot")

chat_history = tk.Text(root)
chat_history.pack()

entry = tk.Entry(root)
entry.pack()

send_button = tk.Button(root, text="Send", command=send_message)
send_button.pack()

root.mainloop()




