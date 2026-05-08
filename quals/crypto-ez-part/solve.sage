import requests
import hashlib
from itertools import product
from tqdm import tqdm
import gmpy2
from Crypto.Util.number import bytes_to_long, long_to_bytes
interesting = 150
BITS = 1536
SET_SIZE = 80


masks = [('0xf054e130bc40c81cca5530e9aa42f610b022639c1688ec55', 889),
         ('0x30be10d48a9756ac16b070b2d8c4b8038850967b4a64d028', 312),
         ('0xaa2855ed1e0608ab148a5124876e58b0589bc02470cae40f', 196),
         ('0x7fd3597410ac065090d630f746058880be4410707b5d0360', 886),
         ('0x50660815cf982494a825b44c9a2ae28167d8058772568e94', 23),
         ('0x21040c9033257eb2966282b0b182183f58c0836b172cc6f5', 280),
         ('0x155378d076d4780c0546566ca24b8690ba144a1d86a1d0c4', 1160),
         ('0xa60146c16e880b97d684e0be078348764ce1401aea8c2712', 1248),
         ('0x41a155f804f1ba6104018c432290e63cd88ec71eaa4c116d', 1247),
         ('0xa5f60608841c82101466ec0562faa5a1c9b19b107336b816', 976),
         ('0x840742810741f9675089628938150437f4699c0a1ad1fe98', 149),
         ('0x4a977323b26d7d3578aa8080b4100d3a2c08416ed881d013', 1284),
         ('0x2842fb2e920a943a24ed5f0aad190010d3109b29678200ef', 1176),
         ('0x8fd56a3304d6c5819e3b304a281886f82010734d80e490d3', 960),
         ('0x4cad3068045cc298952cbb0020325d41ae07a8c6539fcc68', 578),
         ('0x8185b1c815203394cb85668227901190e236505b61176f8f', 665),
         ('0x452d3216c69be1a5ae2612859ac013f9e059e0c848510251', 868),
         ('0x46298028e00b3c6324c403f7cc89245692047adb6715748a', 1261),
         ('0xd4e922e3863041314f7922835d0ef491880cbb4807154605', 352),
         ('0x39c8556a7dc781c82752664123b0b182134007a5a0a32a27', 340),
         ('0x99fc9b401c3e3b0c48a0b1b0ab03d361280a1941a873a231', 361),
         ('0x2f24643ae9084386c591d5732a6818c8636c04983a183d26', 831),
         ('0x756046c07f48f265032225c1e0c0b555e04f1611e61ba280', 1130),
         ('0xed86e6c0054182328835aa50494b832710537875e2956c23', 160),
         ('0xd3a03e0ae718cc4a19c8cbcb89a981423688a7b08ca4d20', 79),
         ('0x1142004454ee1aa5b28a75ce43f8531065444babc2074993', 135),
         ('0xe56c4b540e04af26c6894b6053d0feb091f8c0b00890811c', 769),
         ('0x5182953a425eb6c142d188011de90391b2646c69d42185b3', 1266),
         ('0x1a4ec3c21902c603a0bd578990edce2cd04a0d42e7842b1', 41),
         ('0x1133b0e69eec70a2c0bf4aa0155122710c2c5ba150058d64', 475),
         ('0x55944e53c108d58ec053f451068ad486b5482f1313508127', 283),
         ('0x87003a38a0088cc25ba66db1c84d95a6a602119a53ad0aea', 1341),
         ('0xd272140b0698faa2e1104add453e1620a8cd70cc11581715', 1040),
         ('0x61c214ce70232ca16e3ab845f5f1300a59706260314c3186', 1184),
         ('0xe194314c6bf17521391fe0202c2815b305101dc31596488e', 10),
         ('0x6ed7adb82a538266148602094324a4dea324a09ca0712d70', 874),
         ('0xf1a42548495e0662036cf440b4dab88a6d00581d94b19352', 473),
         ('0x3d1be60e9dd0b926c0c462485d0542010aa879a840ee51c5', 948),
         ('0x3ca00091e01896956546beba54cfed4c202e99aa06300b81', 191),
         ('0xc4c4027e22d663691446eb8b0089c5100ec06b5b80178b37', 917),
         ('0x732c802859a83114938942f4eabf380563070128f9362594', 571),
         ('0xd5812607a10a8b058e9821fd22980bacd56220ca6b0e8786', 723),
         ('0x12602ea96b42aebc882c32153d7583516881f4418582bc14', 1115),
         ('0x963cdc80800e34bf4191658e70164c923864c30fe6c25418', 794),
         ('0x8713207990c2083d53374bc5a3121326ee78853900a46562', 1315),
         ('0x5501612b13590cbd324201cc8d328cf58f825aa29084b555', 560),
         ('0x116da8eb693e4a604fc09adade658a42200ba784119407', 331),
         ('0x20accca807a232572d1f00960e56973814aa6983261fb84', 1017),
         ('0x2a32d350a90368103b82be25c4e0601513f7143cacc81c8d', 785),
         ('0xd8302009d441da0c2aee0611cba511d4200ff200ffdce20e', 292),
         ('0x1bda1a19972126626c056410c1d7f61758c81c5619091494', 90),
         ('0xdac0592380432966212a01560bd1ffc4080cecdc64915b52', 695),
         ('0xe2664153990116a24d553a6f352ac70f212b50200a087b0b', 1258),
         ('0x5b1611487b71b06c43556a0340983a148a6436a45562f81c', 1263),
         ('0xc2250b714cf20f150320a2f0e4842332859286c76ebc2166', 1343),
         ('0x5820d8a619121a23f20ad63f1453146c1506aa69341b7c42', 445),
         ('0xaa82ca21580a0380e5a4259e4c0de620995e64cd4e4c36b4', 1064),
         ('0x992f28c0e3fd15018a022afe35e01fbfa00c78ac8940104', 1305),
         ('0xa19cc71ac011c2ad67b25c1483925805551266c163aca681', 397),
         ('0xf715a008279470182c2408786f246854a4f141f14abaa66c', 452),
         ('0x50a241437b9361c1412d762a00aed4e8c6510e1d3d2b2850', 887),
         ('0x97070b290e3808a44ede231020c1151a3ad384b8370f74d1', 710),
         ('0x806d5c870961c7b83a540978262cd4aa6c10c232ba2446cc', 1112),
         ('0x1159465302e8af8a9b6e0608837de233a8c14b7800482713', 649),
         ('0xb938c67026efa22a15806dd20140122a576e249e6307900e', 662),
         ('0xa650bd929782d84891c684780c2a53286e4c8803d3c889b9', 563),
         ('0x9c50780673178115195064ac0e3637807549b0284e819dba', 13),
         ('0x89e16b42058d28407a19952b88004694aa864e98e347b69e', 541),
         ('0x71ae820482d4320fc2612da2078209694e26076b2495cdcd', 338),
         ('0x1fd9c449c2d3e1a0faabc900d055ed072681461a84608c02', 920),
         ('0x8d7610150ea21c71295d2f14968d4880c472161f120ebe60', 113),
         ('0xded5805e8a0042b2990b04fbbd0046890d07b0e740cb8594', 621),
         ('0x603809dca6499317085580f2ac267e06a813c0fc82c77c2', 709),
         ('0xb32655b61c4d541c14c02fc7251142e0a5c16b301476a038', 1082),
         ('0x410f8941e20471f5bf21d696d0846bb014146c2d362145c0', 299),
         ('0x908871cc819a2ac101d8262040322cfa0dbc7d4fec01347d', 141),
         ('0x636ec2338ec1c011b05ba05193da2cef123d15101499c012', 650),
         ('0x901ad0c84e293849c26aec0254d7bda15cbe86410a1a4990', 632),
         ('0xc243e0c13862c6ebe8828f2d8048c5a41cd1644f5a11dc20', 704),
         ('0x74e18e650107d3c785631a8918356025b62621a46f9cd', 630),
         ('0xb8a708648b4b20ce310554d358b0a47dc14c2d00a5c5b270', 829),
         ('0x203c9da7281134d8123357a963084bea4cdf8738091c00b', 1277),
         ('0x236d196b204645b87bd7108030e7884fb30e0080b23b8d82', 233),
         ('0xb521256c0700313a5031ba070e98ed3e63838d3306844738', 708),
         ('0xbc3e2948185bc5799233f3711baa00044400660d43a58c96', 9),
         ('0x8621ae166bd210022813a345744a3e4cd05be77005d48313', 528),
         ('0x9881dc07918084cfd7387c7f1b174010c0865e8ea418882c', 400),
         ('0x86516e321d1713287b025e297e1ba2196e20410d3241d421', 396),
         ('0x84c48b97442e422bc632570fc1450e9d8ae072217923446', 1343),
         ('0xc16ce018d2b72885c783510d446fe0d90190cd9e1d8500e', 474),
         ('0x24cc9d3a063f81c08de235879500119c931fc4af50688130', 1205),
         ('0x611cb52524548327d6556989aaaca80ac4a1c38087a68f1', 1207),
         ('0x79cae43a010b526a3567a40581e4a86098e6891001d5ddc1', 206),
         ('0x454af36996c288495aab3d1020316e22fc94188e42886135', 735),
         ('0xc0403295b457960e2d41e0eb18a6c273883709fe38404c84', 1049),
         ('0xd5595ce1201a8755d5cc2b844f122aa833b09036e110102d', 204),
         ('0x5f405bc05a840f4c683058931b01cacc00490a9f6ed32a47', 692),
         ('0x7d65c3464ac01dab407c60ce90a06806694e51287d26a019', 430),
         ('0xdd45f442404977c8642171ea6323c7101c0e7b01351a988', 849),
         ('0x515ff302379b13e148c1107880ac85989ae186932c0a7b00', 1214),
         ('0x84410e1e670564b4a32b5c4e082859c20394dcb2adc949a1', 145),
         ('0x898a102ca7da3398361304b5a401999e2669f74342706221', 1060),
         ('0x51a41108a1ebe4da4900e8d0631cc545294d0362a71fa86c', 1344)]

def get_bit_indices(n):
    indices = set()
    i = 0
    while n > 0:
        if n & 1:
            indices.add(i)
        n >>= 1
        i += 1
    return indices
def bits_to_mask(subsets):
    s = []
    for (mask,shift) in (subsets):
        i = 0
        for m in mask:
            i |= 1<<m
        s.append((i,shift))
    return s
def subset_adjust_shift(subset,shift):
    return {x+shift for x in subset}
def count_common_elements(target_set, subsets):
    counts = []

    for mask in subsets:
        common_count = len(target_set & mask)  # Intersection
        counts.append(common_count)

    return counts

def process_masks(pairs):
    subsets = []
    for (hex_val,shift) in pairs:
        val = int(hex_val,16)<<shift
        subsets.append(get_bit_indices(val))
    return subsets


subsets = process_masks(masks)
def parse_errors(error_msg):
    lines = error_msg.split('\n')
    result = {}
    for line in lines:
        if line.startswith('Wrong b: '):
            result['wrong_b'] = int(line.replace('Wrong b: ', ''))
        elif line.startswith('Wrong mask : '):
            parts = line.replace('Wrong mask : ', '').split(',')
            mask_idx = int(parts[0])
            wrong_hash = parts[1]

            if 'wrong_masks' not in result:
                result['wrong_masks'] = {}
            result['wrong_masks'][mask_idx] = wrong_hash
    l = []
    print(result)
    for i in range(len(result["wrong_masks"].keys())):
        l.append(result["wrong_masks"][i])
    result["wrong_masks"] = l
    return result

def hash_value(value):
    return hashlib.sha256(str(value).encode()).hexdigest()

def hash_target(hash_val):
    def momo(t):
        return hash_value(t) == hash_val
    return momo

def bruteforce_hash(bit_true_indices, target_fun, bit_unknown_indices):
    # Start with base value (known 1 bits)
    base_value = 0
    for idx in bit_true_indices:
        base_value |= (1 << idx)

    # Try all combinations of unknown bits
    n_unknown = len(bit_unknown_indices)
    for combo in tqdm(product([0, 1], repeat=n_unknown)):
        test_value = base_value
        for i, bit in enumerate(combo):
            if bit:
                test_value |= (1 << bit_unknown_indices[i])

        if target_fun(test_value):
            return test_value
    assert False, "Bruteforce failed"
URL = "http://localhost:5000"

# Create account
password1 = "yoo"
password2 = "mai"
r = requests.post(f"{URL}/create-account", json={"username": "user1", "password": password1})
print("Create:", r.json())

r = requests.post(f"{URL}/prove-id",json={"username":"user1","password":"f"*191})
b1 = gmpy2.mpz(parse_errors(r.json()['message'])["wrong_b"])

r = requests.post(f"{URL}/create-account", json={"username": "user2", "password": password2})
r = requests.post(f"{URL}/prove-id",json={"username":"user2","password":"g"*191})
b2 = gmpy2.mpz(parse_errors(r.json()['message'])["wrong_b"])

x1 = gmpy2.mpz(bytes_to_long(password1.encode()))
x2 = gmpy2.mpz(bytes_to_long(password2.encode()))
print(x1,x2)
a = gmpy2.mpz(3)
print("pow1")
res1 = pow(a,x1)-b1
print("pow2")
res2 = pow(a,x2)-b2
print("gcding")
almost_p = gmpy2.gcd(res1,res2)
for i in range(2,10000):
    while almost_p % i == 0:
        almost_p //= i
p = Integer(almost_p)
assert is_prime(p)
F = GF(p)
a = F(3)



# Prove identity
r = requests.post(f"{URL}/prove-id", json={"username": "admin", "password": "pass123"})
print("Prove:", r.json())

parsed = parse_errors(r.json()['message'])
print(parsed)
res = F(parsed["wrong_b"])
b = F(int(res))
x_recovered = [None for _ in range(BITS)]
for i in range(interesting):
    print("Testing bit ", i)
    if kronecker(res, p) == 1:  # quadratic residue
        curr_bit = 0
    else:
        curr_bit = 1
        res = F(res * a ^ -1)
    res = res.sqrt()
    x_recovered[i] = curr_bit
known = set(range(150))
hashes = parsed["wrong_masks"]
while len(subsets)>0 and len(known)<BITS:
    commons = count_common_elements(known,subsets)
    print(commons)
    smallest_brute_idx = commons.index(max(commons))
    brute = SET_SIZE - commons[smallest_brute_idx]
    print(brute)
    now_hash = hashes[smallest_brute_idx]
    #mask = masks[smallest_brute_idx]
    #mask = int(mask[0],16)<<mask[1]
    #assert hash_value(mask& x) == now_hash
    bits_to_brute = subsets[smallest_brute_idx] - known
    bits_known = subsets[smallest_brute_idx] & known
    bits_known_true = list(filter(lambda x: x_recovered[x] == 1, bits_known))
    print(bits_known)
    print(bits_to_brute)
    bruteforce_result = bruteforce_hash(bits_known_true,hash_target(now_hash),list(bits_to_brute))
    assert bruteforce_result is not None
    for brute_idx in bits_to_brute:
        x_recovered[brute_idx] = (bruteforce_result & (1<<brute_idx))>> brute_idx
    print(x_recovered)
    known |= bits_to_brute
    subsets.pop(smallest_brute_idx)
    hashes.pop(smallest_brute_idx)
print("Finshed bruteforce hashes!!")
bits_true = [i for (i,b) in enumerate(x_recovered) if b == 1]
bits_to_brute = [i for (i,b) in enumerate(x_recovered) if b is None]
def pow_target(bbbb):
    def momo2(xx):
        return pow(a,xx,p) == bbbb
    return momo2
final_x = bruteforce_hash(bits_true,pow_target(b),bits_to_brute)
# Get secret (will fail without correct x)
r = requests.post(f"{URL}/prove-id", json={"username":"admin","password":long_to_bytes(final_x).decode()})
print("Secret:", r.json())