# Send to single device.
import requests
import json

from django.shortcuts import redirect

from app.models import Bairro


def func():
    MY_API_KEY = "AIzaSyBnlgWoujtti_spHWB12o2WZENKSaeDIY"

    messageTitle = "Pedido Novo Focus Delivery"
    messageBody = "Tem um novo pedido no aplicativo"

    data = {"to": "/topics/dcher",
            "notification": {"body": messageBody, "title": messageTitle, "icon": "ic_cloud_white_4dp",
                             "sound": "default"}}

    dataAsJSON = json.dumps(data)

    resp = requests.post("https://gcm-http.googleapis.com/gcm/send", data=dataAsJSON,
                         headers={"Authorization": "key=" + MY_API_KEY, "Content-type": "application/json"})


def script(request):
    list_names = ['Acacio Figueiredo',
                  'Alameda',
                  'Alto Branco',
                  'Araxa',
                  'Bairro das Cidades',
                  'Bairro das Nacoes',
                  'Bairro Universitario',
                  'Bela Vista',
                  'Bodocongo',
                  'Caatingueira',
                  'Catole',
                  'Centenario',
                  'Centro',
                  'Cinza',
                  'Conceicao',
                  'Cruzeiro',
                  'Cuites',
                  'Dinamerica',
                  'Distrito Industrial',
                  'Estacao Velha',
                  'Gloria',
                  'Itarare',
                  'Jardim Continental',
                  'Jardim Paulistano',
                  'Jardim Tavares',
                  'Jardim Verdejante',
                  'Jeremias',
                  'Joao Paulo II',
                  'Jose Pinheiro',
                  'Lauritzen',
                  'Liberdade',
                  'Ligeiro',
                  'Louzeiro',
                  'Major Veneziano',
                  'Malvinas',
                  'Mirante',
                  'Monte Castelo',
                  'Monte Santo',
                  'Nova Brasilia',
                  'Novo Bodocongo',
                  'Novo Cruzeiro',
                  'Novo Horizonte',
                  'Palmeira',
                  'Palmeira Imperial',
                  'Pedregal',
                  'Portal Sudoeste',
                  'Prata',
                  'Presidente Medici',
                  'Quarenta',
                  'Ramadinha',
                  'Rocha Cavalcante',
                  'Rosa Cruz',
                  'Sandra Cavalcante',
                  'Santa Cruz',
                  'Santa Rosa',
                  'Santo Antonio',
                  'Sao Jose',
                  'Serrotao',
                  'Severino Cabral',
                  'Tambor',
                  'Tres Irmas',
                  'Velame',
                  'Vila Cabral de Santa Rosa',
                  'Vila Cabral de Santa Terezinha']
    for name in list_names:
        b = Bairro(nome=name)
        b.save()
    return redirect('/')
