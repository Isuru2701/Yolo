import requests
from dotenv import load_dotenv
import os

API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
headers = {"Authorization": f"Bearer {os.getenv('HF_SECRET')}"}

#TODO: These values are limited to 10 labels each. As we have 113 labels, lets divide them into categories and query them in batches. If a label is < THRESHOLD, ignore them
def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

labels = ['betrayal',
                  'competition',
                  'bank heist',
                  'neorealism',
                  'no background score',
                  'satire',
                  'robot',
                  'based on comic',
                  'sword and sandal',
                  'biker',
                  'one man army',
                  'blockbuster',
                  'neo noir',
                  'time travel',
                  'remake',
                  'cyberpunk',
                  'multiple perspectives',
                  'vampire',
                  'fantasy sequence',
                  'zombie',
                  'shootout',
                  'conspiracy',
                  'steampunk',
                  'rescue',
                  'wuxia',
                  'robbery',
                  'corruption',
                  'idealism',
                  'director cameo',
                  'anime',
                  'dialogue driven',
                  'epic',
                  'superhero',
                  'cult film',
                  'southern gothic',
                  'futuristic',
                  'ambiguous ending',
                  'slasher',
                  'cult',
                  'medieval times',
                  'organized crime',
                  'ensemble cast',
                  'famous line',
                  'rotoscoping',
                  'post-apocalypse',
                  'plot twist',
                  'chick flick',
                  'tech-noir',
                  'battle',
                  'parenthood',
                  'action hero',
                  'caper',
                  'double cross',
                  'experimental film',
                  'parody',
                  'coming of age',
                  'dream sequence',
                  'high school',
                  'based on comic book',
                  'kidnapping',
                  'redemption',
                  'experimental',
                  'no music',
                  'spirituality',
                  'heist',
                  'alternate history',
                  'flashback',
                  'supernatural',
                  'criminal mastermind',
                  'swashbuckler',
                  "character's point of view camera shot",
                  'farce',
                  'Americana',
                  'dark hero',
                  'investigation',
                  'road movie',
                  'police corruption',
                  'surprise ending',
                  'Shakespeare',
                  'famous score',
                  'nonlinear timeline',
                  'whistleblower',
                  'police detective',
                  'musical number',
                  'dialogue driven storyline',
                  'based on book',
                  'based on novel',
                  'famous opening theme',
                  'femme fatale',
                  'hero',
                  'virtual reality',
                  'deus ex machina',
                  'knight',
                  'dystopia',
                  'psychopath',
                  'monster',
                  'one against many',
                  'postmodern',
                  'espionage',
                  'voice over narration',
                  'on the run',
                  'serial killer',
                  'ninja',
                  'fictional biography',
                  'directed by star',
                  'business',
                  'race against time',
                  'fairy tale',
                  'self sacrifice',
                  'kung fu',
                  'based on play',
                  'anti-hero',
                  'multiple storyline']
output = query({
        "inputs": "Hi, I recently bought a device from your company but it is not working as advertised and I would like to get reimbursed!",
        "parameters": {"candidate_labels": labels}
})
print(output)
