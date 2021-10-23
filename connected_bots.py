import requests
import json
import time


def send_mesagge(msg, sender, port, meta):

    # direccion del localhost en el que se encuentra el servidor de rasa
    url = 'http://localhost:'+str(port)+'/webhooks/rest_custom/webhook'

    #objeto json que se enviara al servidor de rasa
    data = {"sender": sender, "message": msg, "metadata": { "type": meta }}

    #envio mediante post el objeto json al servidor de rasa
    x = requests.post(url, json=data) 
    #obtengo la respuesta del servidor de rasa
    rta = x.json() 

    
    if x.status_code == 200: 
        #si el status es 200, entonces contesto bien
        #retorno el texto de la respuesta
        return rta.pop(0)['text'] 
    else: 
        #si el status no es 200 hubo un error
        #imprimo el error por pantalla
        print(x.raw) 
        return None 



"""
    INSTANCIO EL BOT 1
"""
#puerto del bot 1
p = 5005
#nombre que le voy a dar al bot 1
s1 = "Psybot"
md_s1 = "psybot"


"""
    INSTANCIO EL BOT 2
"""
#puerto del bot 2
#creo que juan va a hacer de bot1 para el model de rasa
p2 = 5005 
#nombre que le voy a dar al bot 2
s2 = "Scrum Assistant"
md_s2 = "scrum_assistant"

rta = send_mesagge("Haceme la entrevista", "Emiliano", p, md_s1)
print(s1 + ': ' + rta)



rta = send_mesagge("no entiendo que es el proceso scrum", "Emiliano", p, md_s2)
print(s2 + ': ' + rta)





"""
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
print("")"""