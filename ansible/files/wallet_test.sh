#!/bin/bash

# Text Colors
NC='\033[0m'		# Text Reset (No color)
BLUE='\033[0;34m'	# Blue
GREEN='\033[0;32m'	# Green
RED='\033[0;31m'	# Red
YELLOW='\033[0;33m'	# Yellow


echo "#################################################################"
echo -e "${BLUE}INFO:${NC} Testing connections to each entry in the Wallet"

CONN_ERRORS=''
. ${HOME}/.bashrc
export TNS_ADMIN=./tns_admin

# Test sqlplus connections to each Credential listed in the tnsnames.ora
declare -a CREDS=(`egrep "^[^#^(]*=$" ${TNS_ADMIN}/tnsnames.ora | cut -d" " -f1`)
for CRED in "${CREDS[@]}"
do
	# Includes "as sysdba" if connecting as SYS user
	if [[ ${CRED} == *"_SYS" ]];
	then
		SYSDBA_SUFFIX='as sysdba'
	else
		SYSDBA_SUFFIX=''
	fi
	
	# Print the command before executing it
	SQLPLUS_CMD="sqlplus -S -L /@${CRED} ${SYSDBA_SUFFIX}"
	echo -e -n "${BLUE}Testing:${NC} ${CRED} ${SYSDBA_SUFFIX}\n"
	sqlplus -S -L /@${CRED} ${SYSDBA_SUFFIX} <<EOF
		whenever sqlerror exit
		set echo off
		set feedback off
		set heading off
		set newpage NONE
		set pages 200
		set verify off
		SELECT 'Connected as user: '||user FROM dual;
		exit;
EOF

	# If sqlplus throws an error, capture the sqlplus test command that generated the error."
	SQL_RETURN_CODE=$?
	if [[ ${SQL_RETURN_CODE} != 0 ]];
	then
		CONN_ERRORS="${CONN_ERRORS}        ${SQLPLUS_CMD}  \n"
	fi
done

echo "#################################################################"

# Print any errors thrown by the sqlplus tests
if [[ ${CONN_ERRORS} == '' ]];
then
	echo -e "${GREEN}SUCCESS:${NC} No errors found for any connection tests"
else
	printf "${RED}ERROR:${NC} The following connection tests produced errors:\n ${CONN_ERRORS}"
fi
