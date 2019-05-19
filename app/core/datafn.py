from app import app, mongo


def encrypt(setpolicy, f):
    enrico = Enrico(policy_encrypting_key=getPolicyKey(setpolicy))
    payload = f.readlines()
    ciphertext, _signature = enrico.encrypt_message(payload)
    return ciphertext

def getPolicyKey(n):
	if n == 1:
		#policy1
		policy1pass = b'ethnewyork'
		policy1_pubkey = ALICE.get_policy_pubkey_from_label(policy1pass)
		policyexpiry =  maya.now() + datetime.timedelta(days=5)
		activepolicy = ALICE.grant(BOB, policy1pass, m=2, n=3, expiration=policyexpiry)
		if activepolicy.public_key == policy1_pubkey:
			print("key 1 is created and in scope")
		return policy1_pubkey
	if n == 2:
		#policy2
		policy2pass = b'ethglobal'
		policy2_pubkey = ALICE.get_policy_pubkey_from_label(policy2pass)
		policyexpiry =  maya.now() + datetime.timedelta(days=5)
		activepolicy = ALICE.grant(BOB, policy2pass, m=2, n=3, expiration=policyexpiry)
		if activepolicy.public_key == policy2_pubkey:
			print("key 2 is created and in scope")
		return policy2_pubkey

