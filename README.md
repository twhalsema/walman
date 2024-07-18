# Walman
## Overview
<b>Walman</b> is a python script which stores information about Oracle wallets in a database and uses that information to generate wallet files, populate them with credentials pulled from 1password.com, and deploy those wallets to desired locations.

In addition to <b>Walman</b> itself - Ansible files, other automations, and documentation - are provided to allow you to test the program with sample data/credentials.

## Glossary
<<incomplete>>

## Installing Walman
<<incomplete>>

## Running Walman
<<incomplete>>

### Main Menu
<<incomplete>>

### Wallets - Create Wallet
<<incomplete>>

### Wallets - Manage Wallet
<<incomplete>>

### Wallets - Manage Wallet - Generate/Deploy Wallet
<<incomplete>>

### Credentials - Manage Credentials
<<incomplete>>



## Walman Demonstration
<<incomplete>>

## Requirements
To use the <b>Walman</b> demo, you will need to have the following in place:
- Three VMs
  - 1 with RHEL8 (dbserver) - 2048GB RAM, 30GB storage
  - 2 with RHEL9 (dbclients1/2) - 2048GB RAM, 20GB storage
  - I intend to provide sometime soon a Bash script which will automatically provision these in VirtualBox.
- Separate Linux host or workstation with Ansible controller configured and able to connect to the 3 VMs without a password and with nopasswd sudo access.
- Account on 1password.com with a vault called <b>wallman_test</b> and a Service Account which has access to make changes in that vault. I have provided a guide on how to do this here: #<<link to the guide here when it's ready>>#
- Update the <b>ansible/vars/walmanvars.yaml</b> file with a value for <b>onepass_token</b> (token for your 1password Service Account).
- Update the <b>ansible/vars/walmanvars.yaml</b> file with a value for <b>ansible_running_account</b> (local account running Ansible on the controller).

## Configure the test environment
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

## Execute Walman
Once you have the lab environment all set up, you're ready to run <b>Walman</b> and give it a try.
To do so, log in to the <b>dbclient1</b> server as the <b>oracle</b> account.
Then run the following:
```bash
python walman.py
```
