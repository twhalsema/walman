FROM ubuntu:24.04

RUN useradd -m -s /bin/bash oracle \
 && echo "oracle:oracle" | chpasswd

ADD --chown=oracle:oracle https://download.oracle.com/otn_software/linux/instantclient/23c/LINUX.X64_234000_client_home.zip /home/oracle/oracle_client/
COPY --chown=oracle:oracle ./ssh_keys /home/oracle/.ssh
COPY --chown=oracle:oracle --chmod=750 ./verify_walman_demo_setup.sh /home/oracle/
ADD --chown=oracle:oracle https://raw.githubusercontent.com/twhalsema/walman/refs/heads/main/walman.py /home/oracle/
ADD --chown=oracle:oracle https://raw.githubusercontent.com/twhalsema/walman/refs/heads/main/demo/files/wallet.tar /home/oracle/wallets/walman_wallet/tns_admin/
ADD --chown=oracle:oracle --chmod=750 https://raw.githubusercontent.com/twhalsema/walman/refs/heads/main/wallet_test.sh /home/oracle/wallets/

RUN apt update && apt install -y curl libaio1t64 openssh-server python3-pip unzip \
 && ln -s /usr/lib/x86_64-linux-gnu/libaio.so.1t64 /usr/lib/x86_64-linux-gnu/libaio.so.1 \
 && sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config \
 && python3 -m pip install --break-system-packages --no-cache-dir colorama onepassword-sdk oracledb paramiko sh

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

RUN unzip /home/oracle/oracle_client/LINUX.X64_234000_client_home.zip -d /home/oracle/oracle_client
RUN tar -xf /home/oracle/wallets/walman_wallet/tns_admin/wallet.tar -C /home/oracle/wallets/walman_wallet/tns_admin
RUN touch /home/oracle/op_var && chmod 600 /home/oracle/op_var
RUN echo 'export ORACLE_HOME=/home/oracle/oracle_client\nexport LD_LIBRARY_PATH=${ORACLE_HOME}/lib\nexport JAVA_HOME=${ORACLE_HOME}/jdk\nexport PATH=${ORACLE_HOME}/bin:${JAVA_HOME}/bin:${PATH}\nexport TNS_ADMIN=/home/oracle/wallets/walman_wallet/tns_admin\n. /home/oracle/op_var\n./verify_walman_demo_setup.sh\n. /home/oracle/op_var' >> /home/oracle/.bashrc
RUN echo 'NAMES.DIRECTORY_PATH=(TNSNAMES,EZCONNECT)\nSQLNET.WALLET_OVERRIDE=TRUE\nWALLET_LOCATION=(SOURCE=(METHOD=FILE)(METHOD_DATA=(DIRECTORY=/home/oracle/wallets/walman_wallet/tns_admin/wallet)))' > /home/oracle/wallets/walman_wallet/tns_admin/sqlnet.ora
RUN echo 'WALMANDB_WALMAN =  (DESCRIPTION = (ADDRESS_LIST = (ADDRESS = (PROTOCOL = TCP)(Host = walmandbserver.example.com )(Port = 1521)))(CONNECT_DATA = (SERVICE_NAME = walmandb)))' > /home/oracle/wallets/walman_wallet/tns_admin/tnsnames.ora


EXPOSE 22

USER root

ENTRYPOINT service ssh start && bash
