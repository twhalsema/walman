# Walman
## Overview
<b>Walman</b> is a python script which stores information about Oracle wallets in a database and uses that information to generate Oracle wallet files, populate them with credentials pulled from 1password.com, and deploy those Oracle wallets to desired servers/directories.

In addition to <b>Walman</b> itself, a [Walman Demo](https://github.com/twhalsema/walman/edit/main/README.md#walman-demo) (Ansible files, other automations, and documentation) is provided to allow you to test the program with sample data/credentials.

## Glossary
The following terms will be used throughout this document.

|Term|Description|
|-----:|---------------|
|Credential|A record stored in the <b>Walman</b> database which represents an Oracle connection string and the 1password entry associated with it. When added to a Wallet, the username/password in the 1password entry will be queried to populate an <b>Oracle wallet</b>.|
|Oracle wallet|An <b>Oracle wallet</b> is a set of files which securely store database login credentials (username/password pairs). Each username/password pair stored in an <b>Oracle wallet</b> is associated with a connection string or an alias name pointing to one. Oracle wallets require their own password in order to create or modify them. Oracle wallets are capable of other functions, but those are outside the scope of <b>Walman</b>.|
|Site|A record stored in the <b>Walman</b> database which repesents a server and directory. When assigned to a <b>Wallet</b>, the generated <b>Oracle wallet</b> will be deployed to that server/directory.|
|Wallet|When the word <b>Wallet</b> is used on its own (instead of <b>Oracle wallet</b>), it is a record stored in the <b>Walman</b> database which represents an Oracle wallet which can be generated and deployed. Each <b>Wallet</b> has a 1password entry associated with it. This is the password used when creating/modifying the <b>Oracle wallet</b>.|

## Install Walman
NOTE: This section is for installing <b>Walman</b> manually. For automated install and sample data population, see [Walman Demo](https://github.com/twhalsema/walman/edit/main/README.md#walman-demo)

There are 2 components to <b>Walman</b>:
1. Walman database
2. walman.py

To set up the <b>Walman</b> database, you will need to have an Oracle database up and running. Steps for how to install Oracle and create a database are outside the scope of this document. Once you have your database up and running, use the <b>Walman Database ERD</b> provided below to build the table structure. Alternatively, the SQL DDL to create the tables can be found in <b>examples/ansible/templates/populate_dbs.j2</b>. Just ignore the INSERT statements.

To install <b>walman.py</b>, copy the file to whatever server you intend to use as your <b>Walman</b> client. 
Then run the following commands to install Python and the necessary packages.
```
dnf install python3
pip install git+https://github.com/1Password/onepassword-sdk-python.git@v0.1.0-beta.9
pip install colorama
pip install oracledb
pip install paramiko
pip install sh
dnf config-manager 
```
Next, install and log in to the 1password CLI using the instructions found here: https://developer.1password.com/docs/cli/get-started/

## Walman Database ERD
![Walman database ERD](/assets/images/walman_erd.png)

## Run Walman
To invoke <b>Walman</b>, run the following:
```
python walman.py
```
This will run the application and present you with the Main Menu.

### Main Menu
|Option|Description|
|-----:|---------------|
|Wallets - Create Wallet|Form for the user to store a new Wallet record. This will not create an actual Oracle wallet yet.|
|Wallets - View/Manage Existing Wallet|Prompts the user to enter a search term and select a Wallet. Presents a menu for the user to view the Wallet's info, modify it, or generate/deploy an Oracle wallet from it.|
|Credentials - Manage Credentials|Presents a menu for additional options for Credentials.|

### Wallets - Create Wallet
|Prompt|Description|
|-----:|---------------|
|Wallet Name / Passmgr Entry|This is the name of the Wallet in Walmgr. It will also be the name of the 1Password entry which stores the password for the Oracle wallet generated later. All Wallets' names start with "WALLET - "|
|Wallet Description|This is just a description the user can use to remember the purpose of the Wallet.|

### Wallets - Manage Wallet
The user will be prompted for a search term. This is just to narrow down the list of Wallets to choose from. Leave the prompt blank to see all Wallets listed if needed. Then select a Wallet from the list.

|Option|Description|
|-----:|---------------|
|View Wallet Details|Lists the Wallet's information (e.g. Name, Description, local directory where an Oracle wallet has been generated for it, Credentials added to it, Sites assigned to it.)|
|Generate/Deploy Wallet|Navigates to a menu with additional options for generating and deploying an actual Oracle wallet for the Wallet.|
|Credentials - Add to Wallet|Form to add Credentials to the Wallet. The Credentials must already have been created via the Credentials - Manage Credentials menu.|
|Credentials - Remove from Wallet|Form to remove Credentials from the Wallet if any have been previously added.|
|Sites - Assign to Wallet|Form to create a Site and assign it to the Wallet.|
|Sites - Unassign from Wallet|Form to unassign a Site from a Wallet and delete it.|
|Delete Wallet|Prompts for confirmation before deleting a Wallet and all of its associated Sites. Credentials are not deleted, but they are removed from the Wallet record.|

### Wallets - Modify Wallet - Assign Site
|Prompt|Description|
|-----:|---------------|
|Site Host Name|The name of a server to which the Oracle wallet should be deployed later.|
|Site Directory|The directory where the Oracle wallet will reside on that server.|
|Site Owner|The os account which will own the Oracle wallet files. The server/account running <b>Walman</b> must be able to ssh to the Site Host Name as Site Owner without a password before deploying the Oracle wallet.|

### Wallets - Generate/Deploy Wallet
|Option|Description|
|-----:|---------------|
|Generate Wallet locally|Gets the Wallet's information, Credentials, and assigned Sites and uses that information to create an Oracle wallet on the local server where <b>Walman</b> is being run.|
|Test remote connectivity/permissions (optional)|Performs a test for all Sites assigned to the Wallet. Logs in as the Site Owner and ensures the Site Directory is writeable.|
|Deploy Wallet remotely|The user must run the <b>Generate Wallet locally</b> option before running this option. Runs the remote connectivity test for all Sites assigned to the Wallet. If the test passes, it copies the Oracle wallet files to each Site. Finally, it performs a test of the Oracle wallet on each Site to ensure the Site can use the Credentials stored in the Oracle wallet.|

### Credentials - Manage Credentials
|Option|Description|
|-----:|---------------|
|Create Credential|Form to create a new Credential. The Credential can later be added to one of more Wallets.|
|Modify Credential|Prompts the user to enter a search term and select a Credential. Presents a form to edit information for a Credential. Changes made will not be reflected in Oracle wallets until they are re-generated and re-deployed.|
|Delete Credential|Prompts the user to enter a search term and select a Credential. Shows details for the Credential and prompts for confirmation before permanently deleting the Credential and its Wallet associations. Changes made will not be reflected in Oracle wallets until they are re-generated and re-deployed.|

### Credentials - Create Credential
|Prompt|Description|
|-----:|---------------|
|Credential Name|The alias name that will be added to the tnsnames.ora deployed with an Oracle wallet.|
|Credential DB Host Name|The DB host name that will be added to the Credential's entry in the tnsnames.ora file deployed with an Oracle wallet.|
|Credential DB Port|The port on which a target DB is running. This will be added to the Credential's entry in the tnsnames.ora file deployed with an Oracle wallet.|
|Credential DB Service Name|The service name on which a target DB is running. This will be added to the Credential's entry in the tnsnames.ora file deployed with an Oracle wallet.|
|Credential Passmgr Entry|The 1password entry which contains the username/password to be stored in an Oracle wallet for this Credential. This entry must already exist in 1password before it can be selected here.|

## Walman Demo
This repo contains the files needed to demonstrate Walman with a test database and sample data/credentials. Once you have all the Requirements listed below in place, you will be able to automatically install/configure the Oracle database needed to store Walman data, create 2 additional databases for Oracle wallet connection tests, populate sample data for Walman, and populate sample credentials in 1password. The automation primarily uses Ansible.

### Requirements
To use the <b>Walman</b> demo, you will need to have the following in place:
- Three VMs
  - 1 with RHEL8 (dbserver) - 2048GB RAM, 30GB storage
  - 2 with RHEL9 (dbclients1/2) - 2048GB RAM, 20GB storage
  - I intend to provide sometime soon a Bash script which will automatically provision these in VirtualBox.
- Separate Linux host or workstation with Ansible controller configured and able to connect to the 3 VMs without a password and with nopasswd sudo access.
- Account on 1password.com with a vault called <b>walman_test</b> and a Service Account which has access to make changes in that vault. I have provided a guide on how to do this here: #<<link to the guide here when it's ready>>#
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
|Oracle server|This is running <b>Oracle Database XE</b> (free version) with 3 PDBs - 1 for the <b>Walman</b> database and 2 for testing Oracle wallets.|
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
