# Send to single device.
import requests
import json


def func():
    MY_API_KEY = "AIzaSyBnlgWoujt6ti_spHWB12o2WZENKSaeDIY"

    messageTitle = "Pedido Novo Focus Delivery"
    messageBody = "Tem um novo pedido no aplicativo"

    data = {"to": "/topics/dcher",
            "notification": {"body": messageBody, "title": messageTitle, "icon": "ic_cloud_white_48dp",
                             "sound": "default"}}

    dataAsJSON = json.dumps(data)

    resp = requests.post("https://gcm-http.googleapis.com/gcm/send", data=dataAsJSON,
                               headers={"Authorization": "key=" + MY_API_KEY, "Content-type": "application/json"})
