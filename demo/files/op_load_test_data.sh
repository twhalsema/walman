#!/bin/bash

. /home/oracle/.bashrc
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
