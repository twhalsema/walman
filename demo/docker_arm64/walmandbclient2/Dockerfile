FROM arm64v8/ubuntu:24.04

RUN useradd -m -s /bin/bash oracle \
 && echo "oracle:oracle" | chpasswd

COPY --chown=oracle:oracle ./ssh_keys /home/oracle/.ssh
ADD --chown=oracle:oracle https://download.oracle.com/otn_software/linux/instantclient/1925000/instantclient-basic-linux.arm64-19.25.0.0.0dbru.zip /home/oracle/
ADD --chown=oracle:oracle https://download.oracle.com/otn_software/linux/instantclient/1925000/instantclient-sqlplus-linux.arm64-19.25.0.0.0dbru.zip /home/oracle/

RUN chmod 600 /home/oracle/.ssh/*

RUN apt update && apt install -y libaio1t64 openssh-server unzip \
 && ln -s /usr/lib/aarch64-linux-gnu/libaio.so.1t64 /usr/lib/aarch64-linux-gnu/libaio.so.1 \
 && sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

USER oracle

RUN unzip -o /home/oracle/instantclient-basic-linux.arm64-19.25.0.0.0dbru.zip -d /home/oracle/oracle_client \
 && unzip -o /home/oracle/instantclient-sqlplus-linux.arm64-19.25.0.0.0dbru.zip -d /home/oracle/oracle_client \
 && ln -s /home/oracle/oracle_client/instantclient_19_25 /home/oracle/oracle_client/instantclient_19_25/lib \
 && echo 'export ORACLE_HOME=/home/oracle/oracle_client/instantclient_19_25\nexport LD_LIBRARY_PATH=${ORACLE_HOME}\nexport PATH=${ORACLE_HOME}:${PATH}\nexport TNS_ADMIN=/home/oracle/wallets/walman_wallet/tns_admin\n' >> /home/oracle/.bashrc

EXPOSE 22

USER root

ENTRYPOINT service ssh start && bash
