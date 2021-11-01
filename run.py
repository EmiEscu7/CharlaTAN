import argparse
import os
import sys
from typing import NoReturn
"""
 Aún no está del todo implementado. Aún así para usar CharlaTAN siga las siguientes instrucciones:
    0. Posicionece en el directorio de Charlatan\
    1. Ejecute: python RASAComponents\charge_bots.py
    2. Ejecute: rasa train
    -- CharlaTAN en este punto está entrenado --
    3. Ejecute en una consola: rasa run actions -p 5055
    4. Ejecute en otra consola: rasa run --enable-api --cors “*” --debug -p 5005
    -- CharlaTAN está esperando request.post en los siguentes URL:
            http://localhost:5005/webhooks/rest_custom/webhook -> Usarlo si se necesita enviar METADATA
            http://localhost:5005/webhooks/rest/webhook        -> Establecido por RASA por defecto
    -- 
    Paso opcional: Si desea probar CharlaTAN. Ejecute en otra consola: python connected_bots.py
"""
def run(args: argparse.Namespace) -> NoReturn:
    """Entry point to CharlaTAN who redirect to RASA's entry point
       args: CLI args
    """ 
    print(str(args))
    import rasa
    rasa.run(**vars(args))

def train(args: argparse.Namespace) -> NoReturn:
    import RASAComponents.charge_bots
    RASAComponents.charge_bots.run()

    import rasa.cli.train
    rasa.cli.train.run_training(args)

