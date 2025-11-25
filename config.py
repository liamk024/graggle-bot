import os, dotenv, json

# Define environment variables and constants
dotenv.load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
WEBSITE_CHECK_INTERVAL = round(float(os.getenv("WEBSITE_CHECK_INTERVAL", 60.0)), 1)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-5-nano')
MAX_RESPONSE_TOKENS = int(os.getenv('MAX_RESPONSE_TOKENS', '512'))

if not (DISCORD_TOKEN and OPENAI_API_KEY):
    raise Exception('Discord and OpenAI API tokens must be set in .env file or environment variables.')

# Generate default dynamic config file
# if not os.path.isfile('dynamic.json'):
#     with open('dynamic.json', 'w') as f:
#         json.dump()

# Function to load dynamic configuration values
def get_dynamic_config(key=None):
    with open('dynamic.json', 'r') as f:
        data = json.load(f)
        if not key: 
            return data
    return data.get(key)

# Function to set dynamic configuration values
def set_dynamic_config(key, value):
    data = get_dynamic_config()
    data[key] = value
    with open('dynamic.json', 'w') as f:
        json.dump(data, f, indent=4)