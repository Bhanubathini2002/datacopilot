import configparser
import os
import yaml


config = configparser.ConfigParser()

def is_root_dir():
    """
    Checks if the current working directory is the root directory of a project 
    by looking for either the "/notebooks" or "/agents" folders.

    Returns:
        bool: True if either directory exists in the current directory, False otherwise.
    """

    print("inside is_root_dir")
    current_dir = os.getcwd()
    print("current dir: ", current_dir)
    notebooks_path = os.path.join(current_dir, "notebooks")
    agents_path = os.path.join(current_dir, "agents")
    
    return os.path.exists(notebooks_path) or os.path.exists(agents_path)


def load_yaml(file_path: str) -> dict:
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


if is_root_dir():
    current_dir = os.getcwd()
    config.read(current_dir + '/config.ini')
    root_dir = current_dir
    print("outside is_root_dir")
else:
    print("inside is_root_dir else condition")
    root_dir = os.path.abspath(os.path.join(os.getcwd(), '..'))
    config.read(root_dir+'/config.ini')

if not 'root_dir' in locals():  # If not found in any parent dir
    raise FileNotFoundError("config.ini not found in current or parent directories.")

print(f'root_dir set to: {root_dir}')


def format_prompt(context_prompt, **kwargs):
    """
    Formats a context prompt by replacing placeholders with values from keyword arguments.
    Args:
        context_prompt (str): The prompt string containing placeholders (e.g., {var1}).
        **kwargs: Keyword arguments representing placeholder names and their values.
    Returns:
        str: The formatted prompt with placeholders replaced.
    """
    return context_prompt.format(**kwargs)




# [CONFIG]
USE_SESSION_HISTORY = config.getboolean('CONFIG', 'USE_SESSION_HISTORY')
VECTOR_STORE = config['CONFIG']['VECTOR_STORE']
LOGGING = config.getboolean('CONFIG','LOGGING')
DESCRIPTION_MODEL = config['CONFIG']['DESCRIPTION_MODEL']
EMBEDDING_MODEL = config['CONFIG']['EMBEDDING_MODEL']
USE_COLUMN_SAMPLES = config.getboolean('CONFIG','USE_COLUMN_SAMPLES')
EXAMPLES = config.getboolean('CONFIG', 'KGQ_EXAMPLES')


#[GCP]
PROJECT_ID =  config['GCP']['PROJECT_ID']


#[BIGQUERY]
BQ_REGION = config['BIGQUERY']['BQ_DATASET_REGION']
BQ_OPENDATAQNA_DATASET_NAME = config['BIGQUERY']['BQ_OPENDATAQNA_DATASET_NAME']
BQ_LOG_TABLE_NAME = config['BIGQUERY']['BQ_LOG_TABLE_NAME']


#[FIRESTORE]
FIRESTORE_REGION = config['CONFIG']['FIRESTORE_REGION']


#[PROMPTS]
PROMPTS = load_yaml(root_dir + '/prompts.yaml')


__all__=["USE_SESSION_HISTORY","VECTOR_STORE","LOGGING","DESCRIPTION_MODEL","EMBEDDING_MODEL","USE_COLUMN_SAMPLES","EXAMPLES",
         "PROJECT_ID",
         "BQ_REGION","BQ_OPENDATAQNA_DATASET_NAME","BQ_LOG_TABLE_NAME",
         "FIRESTORE_REGION",
         "PROMPTS"]