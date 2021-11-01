from os import walk
import os
from typing import NoReturn
import yaml
from rasa.shared.utils.io import read_yaml_file
from ruamel import yaml as yaml
from itertools import chain
from pathlib import Path
"""
    falta agregar comentarios en los yml generados, para que qeuden mas claros a la hora de saber cuando empiezan las base de conocimiento de cada bot
"""
dumper = yaml.YAML()
dumper.width = 4096
dumper.representer.add_representer(
    type(None),
    lambda self, _: self.represent_scalar("tag:yaml.org,2002:null", "null"),
)
yaml_parser = yaml.YAML(typ="safe")
yaml_parser.version = (1,2)
yaml_parser.preserve_quotes = True

def generate_stories(folders):
    new_stories = []
    for folder in folders:
        path = Path("RASAComponents/" + folder + "/data/stories.yml")
        story_specific = read_yaml_file(path)['stories']
        for story in story_specific:
            name_story = story['story']
            steps = []
            for step in story['steps']:
                new_step = {}
                if('intent' in step.keys()):
                    new_step['intent'] = str(folder).lower() + "_" + step['intent']
                else:
                    new_step = step
                steps.append(new_step)
            new_stories.append({"story": name_story, "steps": steps})
    general_stories = {"version": "2.0", "stories": new_stories}
    with open("./data/stories.yml", "w", encoding="utf-8") as outfile:
        dumper.dump(general_stories, outfile)    

def union_responses(prefix, general_responses, new_responses):
    for utter in new_responses.keys():
        new_name = "utter_" + str(prefix).lower() + "_" + utter[6:]
        general_responses[new_name] = new_responses[utter]


def generate_domain(folders: Path):
    new_intents = []
    version = None
    session_config = None
    config = None
    slots = {}
    responses = {}
    actions = []
    first = True
    for folder in folders:
        path = Path("RASAComponents/" + folder + "/domain.yml")
        domain_specific = read_yaml_file(path)
        if first:
            version = domain_specific['version']
            session_config = domain_specific['session_config']
            first = False
        if 'config' in domain_specific.keys() and not config:
            config = domain_specific['config']
        slots = dict(slots, **domain_specific['slots'])
        union_responses(folder, responses, domain_specific['responses'])
        if 'actions' in domain_specific.keys():
            actions += domain_specific['actions']
        for intent in domain_specific['intents']:
            if type(intent) is not dict:
                new_intents.append(str(folder).lower() + "_" + intent)
            else:
                name_intent = str(folder).lower() + "_" + list(intent.keys())[0]
                info_intent = intent[list(intent.keys())[0]]
                new_intents.append({name_intent: info_intent})
    general_domain = {"version": version, "session_config": session_config,
                      'intents': new_intents, 'slots': slots, 'responses': responses,
                      'actions': actions}
    with open("./domain.yml", "w", encoding="utf-8") as outfile:
        dumper.dump(general_domain, outfile) 

def generate_nlu(folders: Path):
    nlu_new={'version': '2.0','nlu':[]}

    for folder in folders:  
        path = Path("RASAComponents/" + folder + "/data/nlu.yml")
        nlu_reading = read_yaml_file(path)  
        for line in nlu_reading['nlu']:
            if 'intent' in line:
                line['intent'] = str(folder).lower()+"_" + line['intent']
            """if 'regex' in line:
                line['regex'] = str(folder).lower()+"_" + line['regex']"""
            """if 'synonym' in line:
                line['synonym'] = line['synonym']"""
            nlu_new['nlu'].append(line)  

    with open("./data/nlu.yml", "w", encoding="utf-8") as outfile:
                dumper.dump(nlu_new, outfile)    

folders = []
for (dirpath, dirnames, filenames) in walk('RASAComponents'):
    folders.extend(dirnames)
    break

def run():
    try:
        generate_nlu(folders)
        generate_stories(folders)
        generate_domain(folders)
        print("Generado correctamente: NLU - STORIES - DOMAIN")
    except Exception as e: #Para
        print(e)

run()