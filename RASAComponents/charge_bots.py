from os import walk
import yaml
from rasa.shared.utils.io import read_yaml_file
from ruamel import yaml as yaml
from itertools import chain
from pathlib import Path
"""
    falta agregar comentarios en los yml generados, para que qeuden mas claros a la hora de saber cuando empiezan las base de conocimiento de cada bot
"""


def generate_nlu(folders): #obsoleto pero por si las dudas lo dejamos
    new_intents = []
    for folder in folders:
        path = folder + "/data/nlu.yml"
        nlu_specific = yaml.full_load(open(path))['nlu']
        for intent in nlu_specific:
            examp = str(intent["examples"]).split('\n')
            examples = []
            for e in examp:
                if e != '':
                    examples.append(e.strip('- '))
            if('intent' in intent.keys()):
                new_intent = {"intent": str(folder).lower() + "_" + intent['intent'], "examples": examples}
            elif ('regex' in intent.keys()):
                new_intent = {"regex": intent['regex'], 'examples': examples}
            elif ('synonym') in intent.keys():
                new_intent = {"synonym": intent['synonym'], 'examples': examples}
            new_intents.append(new_intent)
    general_nlu = {"version": "2.0", "nlu": new_intents}
    with open("../data/nlu.yml", "w") as f:
        file = yaml.dump(general_nlu, f, sort_keys=False, allow_unicode=True)


def generate_stories(folders):
    new_stories = []
    for folder in folders:
        path = folder + "/data/stories.yml"
        story_specific = yaml.full_load(open(path))['stories']
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
    with open("../data/stories.yml", "w") as f:
        yaml.dump(general_stories, f, sort_keys=False)



def generate_domain(folders):
    new_intents = []
    version = None
    session_config = None
    config = None
    slots = {}
    responses = {}
    actions = []
    first = True
    for folder in folders:
        path = folder + "/domain.yml"
        print(path)
        domain_specific = yaml.full_load(open(path, encoding="utf8"))
        if first:
            version = domain_specific['version']
            session_config = domain_specific['session_config']
            first = False
        if 'config' in domain_specific.keys() and not config:
            config = domain_specific['config']
        slots = dict(slots, **domain_specific['slots'])
        responses = dict(responses, **domain_specific['responses'])
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
    with open("../domain.yml", "w") as f:
        yaml.dump(general_domain, f, sort_keys=False)

def concatenateNLU(folders):
    dumper = yaml.YAML()
    dumper.width = 4096
    dumper.representer.add_representer(
        type(None),
        lambda self, _: self.represent_scalar("tag:yaml.org,2002:null", "null"),
    )
    yaml_parser = yaml.YAML(typ="safe")
    yaml_parser.version = (1,2)
    yaml_parser.preserve_quotes = True

    nlu_new={'version': '2.0','nlu':[]}

    for folder in folders:
        path = folder + "/data/nlu.yml"
        nlu_reading = read_yaml_file(path)
        for line in nlu_reading['nlu']:
            if 'intent' in line:
                line['intent'] = 'customizer_' + line['intent']
            if 'regex' in line:
                line['regex'] = 'customizer_' + line['regex']
            if 'synonym' in line:
                line['synonym'] = 'customizer_' + line['synonym']
            nlu_new['nlu'].append(line)
    #cambiar el path de este open por donde se va a guardar el nuevo nlu generado
    with open("d:/Universidad/CharlaTAN/RASAComponents/nluTesting.yml","w", encoding="utf-8") as outfile:
        dumper.dump(nlu_new, outfile)



folders = []
for (dirpath, dirnames, filenames) in walk('.'):
    print(dirnames)
    folders.extend(dirnames)
    break

concatenateNLU(folders)
#generate_nlu(folders)
generate_stories(folders)
generate_domain(folders)
