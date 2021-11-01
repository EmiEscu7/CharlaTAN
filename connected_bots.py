import requests
import json
import time


def send_mesagge(msg, sender, port, meta):

    # direccion del localhost en el que se encuentra el servidor de rasa
    url = 'http://localhost:'+str(port)+'/webhooks/rest_custom/webhook'

    #objeto json que se enviara al servidor de rasa
    personality = {"Neuroticism": 0.1,
                   "Extraversion": 0.9,
                   "Openness": 0.9,
                   "Agreeableness": 0.9,
                   "Conscientiousness": 0.9}

    data = {"sender": sender, "message": msg, "metadata": { "type": meta , "personality": personality}}

    #envio mediante post el objeto json al servidor de rasa
    x = requests.post(url, json=data) 
    #obtengo la respuesta del servidor de rasa
    rta = x.json() 

    
    if x.status_code == 200: 
        #si el status es 200, entonces contesto bien
        #retorno el texto de la respuesta
        if rta:
            return rta.pop(0)['text']
        else:
            return ""
    else: 
        #si el status no es 200 hubo un error
        #imprimo el error por pantalla
        print(x.raw) 
        return None 


choose = ''
bot_dict = { 1: 'Customizer',
             2: 'Psybot',
             3: 'WizzardProfessor',
             4: 'ScrumAssistant'
            }
while(True):
    choose = input("1: Customizer, 2: Psybot, 3: WizzardProfessor, 4: ScrumAssistant ")
    choose = bot_dict[int(choose)]
    msg = input(f"Escribe el siguiente mensaje para {choose}: ")
    rta = send_mesagge(msg, "Matias", 5005, choose)
    print(f"{choose}: {rta}")
    
"""
 test antiguos al 01/11/2021
    
        INSTANCIO EL BOT 1
    
    p = 5005
    md_s1 = "Psybot"

    
        INSTANCIO EL BOT 2
    
    md_s2 = "Customizer"

    
        INSTANCIO EL BOT 3
    
    md_s3 = "wizzardprofessor"

    print("Emiliano: " + "Haceme la entrevista")
    rta = send_mesagge("Haceme la entrevista", "Emiliano", p, md_s1)
    print(md_s1 + ': ' + rta)
    input()
    print()
    time.sleep(2)
    print("Emiliano: " + "He estado trabajando con la tarea {0}")
    rta = send_mesagge("He estado trabajando con la tarea {0}", "Emiliano", p, md_s2)
    print(md_s2 + ': ' + rta)
    print()
    input()
    time.sleep(2)
    print("Emiliano: " + "como funciona el proceso?")
    rta = send_mesagge("como funciona el proceso?", "Emiliano", p, md_s3)
    print(md_s3 + ': ' + rta)

    
    #insatncio 'message' que es el primer mensaje que le voy a enviar al bot
    message = 'Hola, como va?'
    print("")
    print("\033[1;34;47m" + "   " + s1 + ': ' + message)
    print("")

    finish = ["Yo me case y no tenemos pensado tener hijos.", "Estoy casado y tenemos una beba de 5 meses."]

    while message not in finish: 
        #ciclo infinitamente para que los bots se comuniquen
        #llamo a la funcion send_mesagge y le paso el mensaje, el nombre del bot que envia el mensaje y el puerto del bot al que le voy a enviar el mensaje
        message = send_mesagge(message, s1, p2, md_s1)
        print("\033[1;31;47m" + "   " + s2 + ': ' + message)
        print("")
        time.sleep(1)
        #llamo a la funcion send_mesagge y le paso el mensaje, el nombre del bot que envia el mensaje y el puerto del bot al que le voy a enviar el mensaje
        message = send_mesagge(message, s2, p1, md_s2)
        print("\033[1;34;47m" + "   " + s1 + ': ' + message)
        print("")
        time.sleep(1)

    print("\033[1;31;47m" + "   " + s2 + ': Bueno me tengo que ir que se me hace tarde. Un placer volver a verte.')
    print("")
    print("\033[1;34;47m" + "   " + s1 + ': Dale, nos vemos!.')
    print("")
"""
