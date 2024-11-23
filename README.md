# Walman
## Overview
<b>Walman</b> is a Python application which stores information about Oracle wallets in a database and uses that information to generate Oracle wallet files, populate them with credentials pulled from 1password.com, and deploy those Oracle wallets to remote servers/directories. Applications can then use those Oracle wallets to securely connect to Oracle databases without storing cleartext passwords in configuration files.

## Glossary
The following terms will be used throughout this document.

|Term|Description|
|-----:|---------------|
|Credential|A record stored in the <b>Walman</b> database which represents an Oracle connection string and the 1password entry associated with it. When added to a Wallet, the username/password in the 1password entry will be queried to populate an <b>Oracle wallet</b>.|
|Oracle wallet|An <b>Oracle wallet</b> is a set of files which securely store database login credentials (username/password pairs). Each username/password pair stored in an <b>Oracle wallet</b> is associated with a connection string or an alias name pointing to one. Oracle wallets require their own password in order to create or modify them. Oracle wallets are capable of other functions, but those are outside the scope of <b>Walman</b>.|
|Site|A record stored in the <b>Walman</b> database which repesents a server and directory. When assigned to a <b>Wallet</b>, the generated <b>Oracle wallet</b> will be deployed to that server/directory.|
|Wallet|When the word <b>Wallet</b> is used on its own (instead of <b>Oracle wallet</b>), it is a record stored in the <b>Walman</b> database which represents an Oracle wallet which can be generated and deployed. Each <b>Wallet</b> has a 1password entry associated with it. This is the password used when creating/modifying the <b>Oracle wallet</b>.|

## Walman Demo
### DEMO - Overview
This git repo contains the files needed to demonstrate `walman.py` in a simulated environment with sample data/credentials. A [scenario](https://github.com/twhalsema/walman/?tab=readme-ov-file#demo---scenario) is also provided to demonstrate the benefits of <b>Walman</b>. 

><b>WARNING:</b> The files used in the <b>Walman</b> demo should NOT be used in production. To install <b>Walman</b> for production use, please instead use the instructions in the [Install Walman (Manual Method)](https://github.com/twhalsema/walman/?tab=readme-ov-file#install-walman-manual-method) section.

There are 2 methods to install and run the <b>Walman</b> demo:  
1. <b>Docker Containers</b> method - Currently x86_64 only. aarch64 version currently being developed.  
2. <b>Virtual Machines</b> method  

You only need to use one of the above methods to install and run the <b>Walman</b> demo, depending on your own preference.

### DEMO - Installation Pre-Requisites
#### Docker Containers method
To use the <b>Walman</b> demo, you will need to have the following in place:
- [Docker](https://docs.docker.com/engine/install/) installed
- [Docker Compose](https://docs.docker.com/compose/install/) installed
- Account on [1password.com](https://1password.com) with a vault called `walman_test` and a <b>Service Account</b> which has access to make changes in that vault.
  > A guide on how to do this can be found here: [1Password Service Account Configuration](https://github.com/twhalsema/walman/blob/main/OP_SERVICE_ACCOUNT.md)

#### Virtual Machines method
To use the <b>Walman</b> demo, you will need to have the following in place:
- [Ansible](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#installing-and-upgrading-ansible-with-pip) installed on your local machine.
  > For aarch64/ARM64, you must install `ansible-core 2.16.0` specifically due to technical limitation of Oracle Linux 8 (required for Oracle 23ai Free on ARM64).
- [VirtualBox](https://www.virtualbox.org/) <b>(x86_64 only)</b> installed on your local machine.
- [VMWare Fusion](https://blogs.vmware.com/teamfusion/2024/05/fusion-pro-now-available-free-for-personal-use.html) <b>(aarch64/ARM64 only)</b> installed on your local machine.
- [Vagrant](https://developer.hashicorp.com/vagrant/downloads) installed on your local machine.
  > For aarch64/ARM64, at time of writing version 2.4.1 works but 2.4.2 does not. You must also run: `vagrant plugin install vagrant-vmware-desktop`
- Account on [1password.com](https://1password.com) with a vault called `walman_test` and a <b>Service Account</b> which has access to make changes in that vault.
  > A guide on how to do this can be found here: [1Password Service Account Configuration](https://github.com/twhalsema/walman/blob/main/OP_SERVICE_ACCOUNT.md)

### DEMO - Install the Demo
Once you have satisfied the above [Pre-Requisites](https://github.com/twhalsema/walman/blob/main/README.md#demo---installation-pre-requisites), run the following from the repo directory to install the <b>Walman</b> demo.

#### Docker Containers method
```bash
cd demo/docker
docker compose up -d
```

#### Virtual Machines method
<b>NOTE:</b> You will be prompted for your <b>1Password Service Account Token</b> near the end of the `main.yaml` playbook execution.
```bash
cd demo

# x86_64 only:
  vagrant up
# aarch64/ARM64 only:
  ./vagrant_up_aarch64.sh

vagrant ssh-config > /tmp/vagrant_sshconfig.txt
ansible-playbook main.yaml
```
> <b>Troubleshooting:</b>
>
> If you receive an error on the PLAY `Configure /etc/hosts for localhost`, it's likely because you don't have passwordless `sudo` set up on your local machine.
> If that is the case, run the following to continue:
>```bash
>ansible-playbook playbooks/etc_hosts_setup.yaml --ask-become-pass
>ansible-playbook main.yaml
>```

### DEMO - Environment
Once the installation completes, you should have the following:
|Item|Description|
|-----:|---------------|
|Oracle server|This container/server `walmandbserver` is running <b>Oracle Database 23ai Free</b> with 3 PDBs - 1 for the <b>Walman</b> database and 2 for testing Oracle wallets.|
|Walman server|This container/server `walmandbclient1` has the <b>Oracle client</b> as well as the `walman.py` program.|
|Oracle client|This container/server `walmandbclient2` is an additional Oracle client container/VM. This is just here in case you want to test remotely deploying Oracle wallets with `walman.py`.|
|WALMANDB|The `WALMANDB` pluggable database will be populated with some demo data to make trying `walman.py` more useful and intuitive.|
|1Password|Your `walman_test` vault in 1Password will be populated with some demo data to make trying `walman.py` more useful and intuitive.|

### DEMO - Execute walman.py
Once you have the demo environment all set up, you're ready to run `walman.py` and give it a try.  
Do the following to launch `walman.py`:  

#### Docker Containers method
```bash
ssh oracle@172.48.0.122
    # Enter "oracle" at the ssh password prompt.
    # You will then be prompted for your <b>1Password Service Account Token</b> when you log in for the first time.
python3 walman.py
```
> <b>Troubleshooting:</b>
>If you receive an error related to the Oracle database, wait 1-2 minutes for the DB to come up and populate. Then run `python3 walman.py` again.

#### Virtual Machines method
```bash
ssh -F /tmp/vagrant_sshconfig.txt walmandbclient1
sudo su - oracle
python3 walman.py
```

### DEMO - Scenario
This section is provided to walk you through a scenario showing the capability of `walman.py`. In this scenario, you will use `walman.py` to deploy and test an Oracle wallet on a remote server.

<b>Step 1:</b> Run the following from the `demo` directory.
##### Docker Containers method
```bash
ssh oracle@172.48.0.123
    # Enter "oracle" at the ssh password prompt.
ls -la
```
##### Virtual Machines method
```bash
ssh -F /tmp/vagrant_sshconfig.txt walmandbclient2
sudo su - oracle
ls -la
```

Observe that there currently is no `wallets` sub-directory present here.

<b>Step 2:</b> Open another Terminal tab/window on your local machine, and run the following from the `demo` directory.
##### Docker Containers method
```bash
ssh oracle@172.48.0.122
python3 walman.py
```
##### Virtual Machines method
```bash
ssh -F /tmp/vagrant_sshconfig.txt walmandbclient1
sudo su - oracle
python walman.py
```

You will be presented with the `walman.py` <b>MAIN MENU</b>.

<b>Step 3:</b> Select option `2) Wallets - View/Manage Existing Wallet`.  
<b>Step 4:</b> When prompted for a `Search String`, leave it blank and press `ENTER`.  
<b>Step 5:</b> Select `1) WALLET - all_test_dbs_and_users`.  
<b>Step 6:</b> You should now be presented with the <b>MANAGE WALLET</b> menu. Select `1) View Wallet Details`.  
<b>Step 7:</b> Observe the details stored for this Wallet. It contains 8 Credentials, and it is configured to be deployed to 2 Sites.  
<b>Step 8:</b> Select `2) Generate/Deploy Wallet`.  
<b>Step 9:</b> Select `1) Generate Wallet locally`. Enter `y` at the prompt.  
<b>Step 10:</b> Observe the output. You will see an Oracle wallet generated locally on `walmandbclient1` using information retrieved from 1Password. It will also test Oracle database connections using the 8 Credentials stored in the Oracle wallet.  
<b>Step 11:</b> Select `3) Deploy Wallet remotely`.  
<b>Step 12:</b> Observe the output. You will see the Oracle wallet deployed to the 2 Sites listed earlier in <b>Step 7</b>. It will also remotely test Oracle database connections using the 8 Credentials stored in the Oracle wallet from each of the Sites.  
<b>Step 13:</b> Select `q) Quit` to close `walman.py`.  
<b>Step 14:</b> Return to your original Terminal tab/window logged in to `walmandbclient2`. Run the following:  
```bash
ls -la
cd wallets/all_test_dbs_and_users
ls -la *
```
Observe that the Oracle wallet files are now present on this server and directory which had previously been assigned as one of the Sites for this Wallet.

<b>Step 15:</b> Run the following to use the Oracle wallet to test a database connection.
```bash
export TNS_ADMIN=/home/oracle/wallets/all_test_dbs_and_users/tns_admin
sqlplus /@TESTPDB1_TESTUSER12
show con_name;
show user;
```
<b>Step 16:</b> Observe that you have logged in to the `TESTPDB1` database as the `TESTUSER12` user via the Oracle wallet that you remotely deployed from `walman.py`. Congratulations!


### DEMO - Uninstall Walman Demo
If you would like to fully uninstall the <b>Walman</b> demo, run the following from the repo directory.

#### Docker Containers method
```bash
cd demo
./cleaup.sh
```

#### Virtual Machines method
```bash
cd demo
vagrant halt
vagrant destroy
rm /tmp/vagrant_sshconfig.txt
sudo vi /etc/hosts
```
Remove the `walman` entries from `/etc/hosts` on your local machine.

## Install Walman (Manual method)
<b>NOTE:</b> This section is for installing <b>Walman</b> manually. This section assumes that you already have an established Oracle database client/server environment in which you wish to use <b>Walman</b>. If you do not already have this in place, you can simulate an environment and try <b>Walman</b> by using the steps in the [Walman Demo](https://github.com/twhalsema/walman/tree/main?tab=readme-ov-file#walman-demo) section.

There are 3 components to <b>Walman</b>:
1. Walman repository database
2. `wallet_test.sh`
3. `walman.py`

<b>Step 1:</b>
To set up the <b>Walman</b> repository database, you will need to have an Oracle database up and running. Steps for how to install Oracle and create a database are outside the scope of this document. Once you have your database up and running, run the following to create the <b>Walman</b> database structure.
```bash
@walmandb_install.sql
```
Refer to the [Walman Database ERD](https://github.com/twhalsema/walman/blob/main/README.md#walman-database-erd) provided above to verify table structure.

<b>Step 2:</b>
Copy the `wallet_test.sh` file to the `/home/oracle/wallets` directory on whatever server you intend to use as your <b>Walman</b> server. This server must have the full Oracle client installed with access to `sqlplus` and `mkstore` utilities.
This directory will be used by `walman.py` to store locally generated Oracle wallet files. However, if you need to use a different location, instructions will be provided later on how to do this. For now, copy `wallet_test.sh` to whatever directory you will use for this purpose.

<b>Step 3:</b>
Copy the `walman.py` file to your <b>Walman</b> server.

<b>Step 4:</b>
Edit `walman.py` script. In the <b>Global Variables</b> near the top of the script:
- Set the `local_wallets_director` variable to the directory where you placed the `wallet_test.sh` file.
- Set the `walman_vault` variable to the name of your 1Password vault.
- Set the `walman_tns_name` to match the tnsnames.ora entry name for your <b>Walman</b> repository database.
><b>Note:</b>As of 22-Nov-2024, the `walman_tns_name` variable does not work. I will update the code for this in the next week or 2. For now, the <b>Walman</b> repository database tnsnames.ora entry must be called `WALMANDB_WALMAN`.


<b>Step 5:</b>
Run the following commands to install Python and the necessary packages on the <b>Walman</b> server.
```bash
dnf install python3
pip install onepassword-sdk
pip install colorama
pip install oracledb
pip install paramiko
pip install sh
dnf config-manager
```
<b>Step 6:</b>
Install and log in to the 1password CLI using the instructions found here: 1password CLI documentation](https://developer.1password.com/docs/cli/get-started/)

<b>Step 7:</b> Store your <b>1Password Service Account Token</b> in `~/.bashrc`. This may not be secure enough for your organization. If not, explore alternative methods in [1password CLI documentation](https://developer.1password.com/docs/cli/get-started/)
```bash
echo 'export OP_SERVICE_ACCOUNT_TOKEN=<your-1password-token>' >> ~/.bashrc
```

<b>Step 8:</b> Configure an Oracle wallet in `/home/oracle/wallets/walman_wallet` to be used by `walman.py` to connect to your <b>Walman</b> repository database.  
><b>Note:</b>This step is currently missing from this document, and detailed steps will be added here or built directly into the product soon. - TH, 2024-11-21.

<b>Step 9:</b> [Run Walman](https://github.com/twhalsema/walman/edit/main/README.md#run-walman)

## Walman Database ERD
![Walman database ERD](/docimages/walman_erd.png)

## Run Walman
To invoke `walman.py`, run the following:
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
|Site Owner|The os account which will own the Oracle wallet files. The server/account running `walman.py` must be able to ssh to the Site Host Name as Site Owner without a password before deploying the Oracle wallet.|

### Wallets - Generate/Deploy Wallet
|Option|Description|
|-----:|---------------|
|Generate Wallet locally|Gets the Wallet's information, Credentials, and assigned Sites and uses that information to create an Oracle wallet on the local server where `walman.py` is being run.|
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
