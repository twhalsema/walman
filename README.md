# Thomas Halsema - Professional Portfolio
## Welcome
Thank you for visiting my professional portfolio. I have prepared this repository as a way to showcase my skillset.
This portfolio is a work in progress, and I intend to include additional automations and enhancements to it in the coming weeks.

At the time of writing (July 2024), I am currently looking for a new job. I have been an Oracle DBA for over 12 years, and I am ready to try something new. Over the last several months, I have been learning skills aligned with the following positions:

- Site Reliability Engineer
- DevOps Engineer
- Infrastructure Engineer

I encourage anyone considering me for employment to look over this portfolio to make a more informed hiring decision.

## What is in this portfolio?
This portfolio consists of 3 parts:
1. <b>Walman</b> (short for Wallet Manager) - A Python program which allows the user to declaratively define Oracle wallets (database credential stores), populate them with credentials from 1password.com, and deploy the wallets to remove database client servers. (This allows centralized management of DB connection info for services to allow for easier password rotation.)
3. Ansible and other automation files to create a test environment to demo <b>Walman</b>.
4. Documentation for <b>Walman</b>. This is both to allow anyone viewing my portfolio to better understand it as well as to highlight my technical writing ability.

Please note that I have not used AI in the creation of any of the files found in this portfolio.

## What skills does this portfolio demonstrate?
In alphabetical order, not by importance:
|Skill|Sub-skill|
|-----:|---------------|
|Ansible|Conditionals, Loops, Playbooks, Templates, Vault, Variables|
|Bash|Data structures, File manipulation|
|Linux|Automation, Environment, Installation, Networking, Security|
|Oracle database|DDL, DML, Installation, Multi-tenancy, Security, SQL, SQLnet, Wallets|
|Python|Database queries, Data structures, File manipulation, SSH connections, User interface|
|Technical Writing||

## How to use this portfolio
Please feel free to just look at the code I have prepared. However, if you would like to actually try out <b>Walman</b> for yourself, please follow these steps to get it up and running on your own lab environment.

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
For full instructions on how to use Walman, please see this document: #<<link to the document here when it's ready>>#
