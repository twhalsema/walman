#!/usr/bin/bash

while [[ ${OP_SERVICE_ACCOUNT_TOKEN} == '' ]];
do
	read -p "[PROMPT] Enter your 1Password service account token: " OP_TOKEN

	echo "[INFO] Populating /home/oracle/op_var with 1Password service account."
	echo "export OP_SERVICE_ACCOUNT_TOKEN=${OP_TOKEN}" > /home/oracle/op_var
	export OP_SERVICE_ACCOUNT_TOKEN=${OP_TOKEN}
done

echo "[INFO] Verifying 1Password vault access."
OP_VAULT_VERIFY=`op vault list | grep walman_test | tr -s ' ' | cut -d' ' -f2`
echo "[INFO] OP_VAULT_VERIFY = ${OP_VAULT_VERIFY}"
if [[ ${OP_VAULT_VERIFY} != 'walman_test' ]];
then
	echo "[ERROR] The walman_test 1Password vault does not exist in the entered 1Password account. Please log out of this server, create the walman_test vault, and reconnect to this server."
	exit
fi

echo "[INFO] Verifying if 1Password demo data already loaded or not."
OP_ITEM_COUNT=`op item list --vault=walman_test | grep -v EDITED | wc -l`

if [[ ${OP_ITEM_COUNT} < 10 ]];
then
	op item create --title="ORACLE - TESTPDB1 - TESTUSER11" --category=login --tags=oracle --vault=walman_test username=testuser11 password=testuserpass1100
	op item create --title="ORACLE - TESTPDB1 - TESTUSER12" --category=login --tags=oracle --vault=walman_test username=testuser12 password=testuserpass1200
	op item create --title="ORACLE - TESTPDB1 - TESTUSER13" --category=login --tags=oracle --vault=walman_test username=testuser13 password=testuserpass1300
	op item create --title="ORACLE - TESTPDB1 - TESTUSER14" --category=login --tags=oracle --vault=walman_test username=testuser14 password=testuserpass1400
	op item create --title="ORACLE - TESTPDB2 - TESTUSER21" --category=login --tags=oracle --vault=walman_test username=testuser21 password=testuserpass2100
	op item create --title="ORACLE - TESTPDB2 - TESTUSER22" --category=login --tags=oracle --vault=walman_test username=testuser22 password=testuserpass2200
	op item create --title="ORACLE - TESTPDB2 - TESTUSER23" --category=login --tags=oracle --vault=walman_test username=testuser23 password=testuserpass2300
	op item create --title="ORACLE - TESTPDB2 - TESTUSER24" --category=login --tags=oracle --vault=walman_test username=testuser24 password=testuserpass2400
	op item create --title="WALLET - all_test_dbs_and_users" --category=login --tags=wallet --vault=walman_test username="WALLET - all_test_dbs_and_users" password=Temporary2Wal
	op item create --title="WALLET - testpdb1_users" --category=login --tags=wallet --vault=walman_test username="WALLET - testpdb1_users" password=Temporary3Wal
fi 

echo "[INFO] Configuring .ssh/known_hosts"
ssh -f -o StrictHostKeyChecking=accept-new oracle@walmandbclient1.example.com 'exit'
ssh -f -o StrictHostKeyChecking=accept-new oracle@walmandbclient2.example.com 'exit'

echo "[########################################################################]"
echo "[############################### WARNING ################################]"
echo "[########################################################################]"
echo "[### This container is for demo purposes only.                        ###]"
echo "[### Do not use this container in production under any circumstances. ###]"
echo "[### This container is not secure.                                    ###]"
echo "[########################################################################]"
echo "[############################### WARNING ################################]"
echo "[########################################################################]"
