# TripleCheck - Anti Deepfakes/Fake News through provenance networks

TripleCheck implements content publishing, encryption/decryption, and verification of published content. Users can login/signup using Fortmatic for easy on-boarding. Users can then create encryption policies for the content they produce. The publishers can then grant access to users in the platform with a set expiry date or publish directly to decentralized outlets like IPFS, Swarm. Platform members can verify hashes for privately shared content. The public can verify hashes for all TripleCheck enabled content that is published over the social medias, referenced in articles or news publications.

### Prerequisites

Step 1: Install Virtualenv and Make a NuCypher Directory
First, we will update our apt-get, then we will install the module virtualenv module.

```
apt-get update
```
```
apt-get install python-virtualenv
```
```
mkdir nucypher
```

Step 2: Create a Virtual Environment & Install Python 3

Virtualenv works by creating a folder that houses the necessary Python executables in the bin directory. In this instance, we are installing Python 3.5 while also creating two folders, the virtualenvironment, and project_1 directory.

```
virtualenv -p /usr/bin/python3 nucypher
```

Virtualenv will create the necessary directories into the project_1 directory. In this directory you’ll find bin, include, lib, local and share.

### Installing

Clone the repo. This is the NuCypher Backend. This assumes that you have a local_fleet with a lonely ursula and a local ursula fleet up and running.

```
git clone https://github.com/harishperfect/triplecheck.git
```

Get into the directory

```
cd triplecheck
```

Install the PIP dependencies

```
pip install -r requirements.txt
```

Finally run the Flask Server

```
python index.py &
```

This will expose the following endpoints

```
/upload - To upload and select the relavant policy
/decrypt - To decrypt the files listed on Explorer
/policy - To create new policies
/verify - To verify if a hash is present and valid
/listEncryptedFiles - Shows all encrypted files on Explorer
/listPublicFiles - Shows all public files on Explorer
```

### DEMO URL

 [Upload Endpoint](http://ec2-18-204-34-34.compute-1.amazonaws.com:5000/upload)
 
 
 [Decrypt Endpoint](http://ec2-18-204-34-34.compute-1.amazonaws.com:5000/decrypt) 
 
The default demo policies are set with the following passwords

policy 1 = ethnewyork
policy 2 = ethglobal

Both have a 30 day expiry set on it.
