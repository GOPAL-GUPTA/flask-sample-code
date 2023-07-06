from flask import Flask, request
import requests
import json

app = Flask("whatsappBusinessBot")

# Configuration file
with open  ('config.json') as f:
    config = json.load(f)
app.config.update(config)

def send_msg(msg, to_number, phone_number_id):
   headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {app.config['ACCESS_TOKEN']}",
   }
   json_data = {
       'messaging_product': 'whatsapp',
       'to': to_number,
       'type': 'text',
       "text": {
           "body": "Thank You for your message"+msg
       }
   }
   url = f"https://graph.facebook.com/{app.config['VERSION']}/{phone_number_id}/messages"
   response = requests.post(url=url, headers=headers, json=json_data)

   print('log:-----------------------------------------------------response.text')
   print(response.text)
   

# webhook verification
@app.route("/webhook", methods=["GET"])
def verify_webhook():
   print(request) 
   if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
       if not request.args.get("hub.verify_token") == app.config["WEBHOOK_TOKEN"]:
            print(request.args.get("hub.verify_token"))
            return "Verification token missmatch", 403
       return request.args['hub.challenge'], 200
   return "Bad Request", 400
 
# Handle messages (send and receive)
@app.route("/webhook", methods=["POST"])
def handle_message():
    # Parse the request body from the POST
    body = request.get_json()

    # Check the Incoming webhook message
    print(json.dumps(body, indent=2))

    if body.get("object"):
        if body.get("entry") and body["entry"][0].get("changes"):
            change = body["entry"][0]["changes"][0]
            if change.get("value").get("messages"):
                phone_number_id = change["value"]["metadata"]["phone_number_id"]
                from_number = change["value"]["messages"][0]["from"]
                msg_body = change["value"]["messages"][0]["text"]["body"]
                customer_name = change["value"]["contacts"][0]["profile"]["name"]
                
                send_msg(msg=msg_body, to_number=from_number, phone_number_id=phone_number_id)
    return "OK", 200

if __name__ == "__main__":
   # app.run(ssl_context='adhoc')
   app.run()