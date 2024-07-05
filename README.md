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
1. <b>Walman</b> (short for Wallet Manager) - A python program which allows the user to declaratively build Oracle wallets (database credential stores) and deploy them to remove database client servers.
2. Ansible and other automation files to create a test environment to demo <b>Walman</b>.
3. Documentation for <b>Walman</b>. This is both to allow anyone viewing my portfolio to better understand it as well as to highlight my technical writing ability.

## What skills does this portfolio demonstrate?
In alphabetical order, not by importance:
|Skill|Sub-skill|
|-----:|---------------|
|Ansible|Conditionals, Loops, Playbooks, Templates, Vault, Variables|
|Bash|Data structures, File manipulation|
|Linux|Automation, Environment, Installation, Networking, Security|
|Oracle database|DDL, DML, Installation, Multi-tenancy, Security, SQL, SQLnet, Wallets|
|Python|Database queries, Data structures, File manipulation, SSH connections, User interface|

## How to use this portfolio
Please feel free to just look at the code I have prepared. However, if you would like to actually try out <b>Walman</b> for yourself, please follow these steps to get it up an running on your own lab environment.

### Requirements/Assumptions
To use the <b>Walman</b> demo, you will need to have the following in place:
- Three VMs - 2 with RHEL9 and 1 with RHEL8. I intend to provide sometime soon a Bash script which will automatically provision these in VirtualBox.
- Separate Linux host or workstation with Ansible configured and able to connect to the 3 VMs without a password and with nopasswd sudo access.

### Configure the test environment
Once you have the above requirements in place, the Ansible project I have provided will take care of the rest. But before you use it, update the <b>inventory</b> file with the names of your hosts. The dbserver should be the RHEL8 VM. The two dbclient servers should be RHEL9.



