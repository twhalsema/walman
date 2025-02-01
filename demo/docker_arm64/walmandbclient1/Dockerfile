FROM arm64v8/ubuntu:24.04

RUN useradd -m -s /bin/bash oracle \
 && echo "oracle:oracle" | chpasswd

COPY --chown=oracle:oracle ./ssh_keys /home/oracle/.ssh
COPY --chown=oracle:oracle --chmod=750 ./verify_walman_demo_setup.sh /home/oracle/
ADD --chown=oracle:oracle https://raw.githubusercontent.com/twhalsema/walman/refs/heads/main/walman.py /home/oracle/
ADD --chown=oracle:oracle https://raw.githubusercontent.com/twhalsema/walman/refs/heads/main/walman.conf /home/oracle/
ADD --chown=oracle:oracle https://raw.githubusercontent.com/twhalsema/walman/refs/heads/main/demo/files/wallet.tar /home/oracle/wallets/walman_wallet/tns_admin/
ADD --chown=oracle:oracle --chmod=750 https://raw.githubusercontent.com/twhalsema/walman/refs/heads/main/wallet_test.sh /home/oracle/wallets/
ADD --chown=oracle:oracle https://download.oracle.com/otn_software/linux/instantclient/1925000/instantclient-basic-linux.arm64-19.25.0.0.0dbru.zip /home/oracle/
ADD --chown=oracle:oracle https://download.oracle.com/otn_software/linux/instantclient/1925000/instantclient-sqlplus-linux.arm64-19.25.0.0.0dbru.zip /home/oracle/
ADD --chown=oracle:oracle https://download.oracle.com/otn_software/java/sqldeveloper/sqlcl-24.3.1.311.1631.zip /home/oracle/

RUN chmod 600 /home/oracle/.ssh/*

RUN apt update && apt install -y curl default-jdk libaio1t64 openssh-server python3 python3-pip unzip \
 && ln -s /usr/lib/aarch64-linux-gnu/libaio.so.1t64 /usr/lib/aarch64-linux-gnu/libaio.so.1 \
 && sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config \
 && python3 -m pip install --break-system-packages --no-cache-dir colorama oracledb paramiko sh onepassword-sdk

RUN curl -sS https://downloads.1password.com/linux/keys/1password.asc | \
    gpg --dearmor --output /usr/share/keyrings/1password-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/1password-archive-keyring.gpg] https://downloads.1password.com/linux/debian/$(dpkg --print-architecture) stable main" | \
    tee /etc/apt/sources.list.d/1password.list && \
    mkdir -p /etc/debsig/policies/AC2D62742012EA22/ && \
    curl -sS https://downloads.1password.com/linux/debian/debsig/1password.pol | \
    tee /etc/debsig/policies/AC2D62742012EA22/1password.pol && \
    mkdir -p /usr/share/debsig/keyrings/AC2D62742012EA22 && \
    curl -sS https://downloads.1password.com/linux/keys/1password.asc | \
    gpg --dearmor --output /usr/share/debsig/keyrings/AC2D62742012EA22/debsig.gpg && \
    apt update && apt install 1password-cli

USER oracle

RUN unzip -o /home/oracle/instantclient-basic-linux.arm64-19.25.0.0.0dbru.zip -d /home/oracle/oracle_client \
 && unzip -o /home/oracle/instantclient-sqlplus-linux.arm64-19.25.0.0.0dbru.zip -d /home/oracle/oracle_client \
 && unzip -o /home/oracle/sqlcl-24.3.1.311.1631.zip -d /home/oracle/oracle_client/instantclient_19_25 \
 && ln -s /home/oracle/oracle_client/instantclient_19_25 /home/oracle/oracle_client/instantclient_19_25/lib \
 && echo '#!/bin/bash\nSQLCL=/home/oracle/oracle_client/instantclient_19_25/sqlcl/lib\nCLASSPATH=${SQLCL}/oraclepki.jar:${SQLCL}/osdt_core.jar:${SQLCL}/osdt_cert.jar\njava -classpath ${CLASSPATH} oracle.security.pki.OracleSecretStoreTextUI  "$@"' > /home/oracle/oracle_client/instantclient_19_25/mkstore \
 && chmod 750 /home/oracle/oracle_client/instantclient_19_25/mkstore \
 && tar -xf /home/oracle/wallets/walman_wallet/tns_admin/wallet.tar -C /home/oracle/wallets/walman_wallet/tns_admin \
 && touch /home/oracle/op_var \ 
 && chmod 600 /home/oracle/op_var \
 && echo 'export ORACLE_HOME=/home/oracle/oracle_client/instantclient_19_25\nexport LD_LIBRARY_PATH=${ORACLE_HOME}\nexport PATH=${ORACLE_HOME}:${PATH}\nexport TNS_ADMIN=/home/oracle/wallets/walman_wallet/tns_admin\n. /home/oracle/op_var\n./verify_walman_demo_setup.sh\n. /home/oracle/op_var' >> /home/oracle/.bashrc \
 && echo 'NAMES.DIRECTORY_PATH=(TNSNAMES,EZCONNECT)\nSQLNET.WALLET_OVERRIDE=TRUE\nWALLET_LOCATION=(SOURCE=(METHOD=FILE)(METHOD_DATA=(DIRECTORY=/home/oracle/wallets/walman_wallet/tns_admin/wallet)))' > /home/oracle/wallets/walman_wallet/tns_admin/sqlnet.ora \
 && echo 'WALMANDB_WALMAN =  (DESCRIPTION = (ADDRESS_LIST = (ADDRESS = (PROTOCOL = TCP)(Host = walmandbserver.example.com )(Port = 1521)))(CONNECT_DATA = (SERVICE_NAME = walmandb)))' > /home/oracle/wallets/walman_wallet/tns_admin/tnsnames.ora

EXPOSE 22

USER root

ENTRYPOINT service ssh start && bash
