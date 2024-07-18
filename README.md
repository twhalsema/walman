# Walman
## Overview
<b>Walman</b> is a python script which stores information about Oracle wallets in a database and uses that information to generate wallet files, populate them with credentials pulled from 1password.com, and deploy those wallets to desired locations.

In addition to <b>Walman</b> itself - Ansible files, other automations, and documentation - are provided to allow you to test the program with sample data/credentials.

## Glossary
The following terms will be used throughout this document.

|Term|Description|
|-----:|---------------|
|Credential|A record stored in the <b>Walman</b> database which represents an Oracle connection string and the 1password entry associated with it. When added to a Wallet, the username/password in the 1password entry will be queried to populate an <b>Oracle wallet</b>.|
|Oracle wallet|An <b>Oracle wallet</b> is a set of files which securely store database login credentials (username/password pairs). Each username/password pair stored in an <b>Oracle wallet</b> is associated with a connection string or an alias name pointing to one. Oracle wallets require their own password in order to create or modify them. Oracle wallets are capable of other functions, but those are outside the scope of <b>Walman</b>.|
|Site|A record stored in the <b>Walman</b> database which repesents a server and directory. When assigned to a <b>Wallet</b>, the generated <b>Oracle wallet</b> will be deployed to that server/directory.|
|Wallet|When the word <b>Wallet</b> is used on its own (instead of <b>Oracle wallet</b>), it is a record stored in the <b>Walman</b> database which represents an Oracle wallet which can be generated and deployed. Each <b>Wallet</b> has a 1password entry associated with it. This is the password used when creating/modifying the <b>Oracle wallet</b>.|

## Install Walman
There are 2 components to Walman:
1. Walman database
2. walman.py

To set up the Walman database, you will need to have an Oracle database up and running. Steps for how to install Oracle and create a database are outside the scope of this document. Once you have your database up and running, use the <b>Walman database ERD</b> provided below to build the table structure. Alternatively, the SQL DDL to create the table can be found in examples/ansible/templates/populate_dbs.j2. Just ignore the INSERT statements.

To install <b>walman.py</b>, simply copy it to whatever server you intend to use as your Walman client. 
Then run the following commands to install Python and the necessary packages. Alternatively, you can use the Ansible code in the Walman Demonstration below to install these components.
```
dnf install python3
pip install git+https://github.com/1Password/onepassword-sdk-python.git@v0.1.0-beta.9
pip install colorama
pip install oracledb
pip install paramiko
pip install sh
```

## Walman Database ERD
[incomplete]

## Run Walman
[incomplete]

### Main Menu
[incomplete]

### Wallets - Create Wallet
[incomplete]

### Wallets - Manage Wallet
[incomplete]

### Wallets - Manage Wallet - Generate/Deploy Wallet
[incomplete]

### Credentials - Manage Credentials
[incomplete]



## Walman Demonstration
[incomplete]

### Requirements
To use the <b>Walman</b> demo, you will need to have the following in place:
- Three VMs
  - 1 with RHEL8 (dbserver) - 2048GB RAM, 30GB storage
  - 2 with RHEL9 (dbclients1/2) - 2048GB RAM, 20GB storage
  - I intend to provide sometime soon a Bash script which will automatically provision these in VirtualBox.
- Separate Linux host or workstation with Ansible controller configured and able to connect to the 3 VMs without a password and with nopasswd sudo access.
- Account on 1password.com with a vault called <b>wallman_test</b> and a Service Account which has access to make changes in that vault. I have provided a guide on how to do this here: #<<link to the guide here when it's ready>>#
- Update the <b>ansible/vars/walmanvars.yaml</b> file with a value for <b>onepass_token</b> (token for your 1password Service Account).
- Update the <b>ansible/vars/walmanvars.yaml</b> file with a value for <b>ansible_running_account</b> (local account running Ansible on the controller).

### Configure the test environment
Once you have the above requirements in place, the Ansible project I have provided will take care of the rest. But before you use it, update the <b>inventory</b> file with the names of your hosts. The dbserver should be the RHEL8 VM. The two dbclient servers should be RHEL9.
Then just run the following:
```bash
ansible-playbook main.yaml
```
Once it completes, you should have the following: 
|Item|Description|
|-----:|---------------|
|Oracle server|This is running <b>Oracle Database XE</b> (free version) with 3 PDBs - 1 for the Walman repository and 2 for testing Oracle wallets.|
|Walman server|This is the <b>dbclient1</b>. It has the <b>Oracle client</b> as well as the <b>walman.py</b> program.|
|Oracle client|This is an additional dbclient server. This is just here in case you want to demo <b>Walman</b> and remotely deploy/test your own Oracle wallet.|
|WALMANDB|The <b>WALMANDB</b> pluggable database will be populated with some demo data to make trying <b>Walman</b> more useful and intuitive.|
|1Password|Your <b>walman_test</b> vault in <b>1Password</b> will be populated with some demo data to make trying <b>Walman</b> more useful and intuitive.|

### Execute Walman
Once you have the lab environment all set up, you're ready to run <b>Walman</b> and give it a try.
To do so, log in to the <b>dbclient1</b> server as the <b>oracle</b> account.
Then run the following:
```bash
python walman.py
```
