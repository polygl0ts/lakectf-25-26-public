import string

from flask import Flask, request, jsonify
import hashlib
import random
from Crypto.Util.number import getPrime, isPrime, bytes_to_long

app = Flask(__name__)

def gen_p(BITS):
    while True:
        q = getPrime(BITS - 150)
        p = q << 150 + 1
        if isPrime(p):
            return p


# Fixed cryptographic parameters
BITS = 1535
a = 3

# prime_p is also generated with gen_p(BITS)
try:
    from flag import prime_p, FLAG, MASKS
    p = prime_p
    flag = FLAG
    # Each mask selects 80 random bits from a cluster of ~200 bits
    masks = MASKS
except:
    print("Running on local")
    p = gen_p(BITS)
    flag = "redacted"
    masks = [('0xf054e130bc40c81cca5530e9aa42f610b022639c1688ec55', 889)]


users_db = {}


def hash_value(value):
    return hashlib.sha256(str(value).encode()).hexdigest()


def verify(x, b, hashes):
    s = ""
    # Verify discrete log
    computed_b = pow(a, x, p)
    if computed_b != b:
        s += f"Wrong b: {b}\n"

    # Verify mask hashes
    for idx in range(len(masks)):
        hex_val, shift = masks[idx]
        mask = int(hex_val, 16) << shift

        masked_value = x & mask
        computed_hash = hash_value(masked_value)
        if computed_hash != hashes[idx]:
            s += f"Wrong mask : {idx},{hashes[idx]}\n"
    if s == "":
        return True, "Valid password"
    else:
        return False, s


def register_user(username, x):
    b = pow(a, x, p)
    mask_hashes = []
    for (hex_val, shift) in masks:
        mask = int(hex_val, 16) << shift
        masked_value = x & mask
        mask_hash = hash_value(masked_value)
        mask_hashes.append(mask_hash)

    users_db[username] = {
        'b': b,
        'mask_hashes': mask_hashes
    }


@app.route('/create-account', methods=['POST'])
def create_account():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400
    if username in users_db:
        return jsonify({"error": "User already exists"}), 400
    x = bytes_to_long(password.encode()) % (p-1)
    register_user(username, x)

    return jsonify({
        "message": f"Account created for {username}",
    }), 201


@app.route('/prove-id', methods=['POST'])
def prove_id():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username:
        return jsonify({"error": "Username required"}), 400

    if not password:
        return jsonify({"error": "Password required"}), 400

    # Check if user exists
    if username not in users_db:
        return jsonify({"error": "no such user found"}), 404

    user_data = users_db[username]
    stored_b = user_data['b']
    stored_mask_hashes = user_data['mask_hashes']
    x = bytes_to_long(password.encode()) % (p-1)
    verification = verify(x, stored_b, stored_mask_hashes)
    if verification[0] and username == "admin":
        verification = (True, FLAG)
    return jsonify({
        "message": verification[1]
    }), (401 if not verification[0] else 200)


# Its basically the password anyways
@app.route('/pwds', methods=['POST'])
def passwords():
    data = request.get_json()
    mask_id = data.get('id')
    if mask_id:
        return jsonify({mask_id: masks[mask_id]}), 400
    return jsonify({"masks?": masks}), 200


if __name__ == '__main__':
    admin_password = ''.join(random.choices(string.ascii_letters+string.digits, k=BITS//8 - 1))
    register_user("admin", bytes_to_long(admin_password.encode()))
    app.run(debug=True, host='0.0.0.0', port=5000)
