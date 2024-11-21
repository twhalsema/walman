FROM ubuntu:24.04

RUN useradd -m -s /bin/bash oracle \
 && echo "oracle:oracle" | chpasswd

ADD --chown=oracle:oracle https://download.oracle.com/otn_software/linux/instantclient/23c/LINUX.X64_234000_client_home.zip /home/oracle/oracle_client/
COPY --chown=oracle:oracle ./ssh_keys /home/oracle/.ssh

RUN apt update && apt install -y libaio1t64 openssh-server unzip \
 && ln -s /usr/lib/x86_64-linux-gnu/libaio.so.1t64 /usr/lib/x86_64-linux-gnu/libaio.so.1 \
 && sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config


USER oracle

RUN unzip /home/oracle/oracle_client/LINUX.X64_234000_client_home.zip -d /home/oracle/oracle_client
RUN echo 'export ORACLE_HOME=/home/oracle/oracle_client\nexport LD_LIBRARY_PATH=${ORACLE_HOME}/lib\nexport JAVA_HOME=${ORACLE_HOME}/jdk\nexport PATH=${ORACLE_HOME}/bin:${JAVA_HOME}/bin:${PATH}\n' >> /home/oracle/.bashrc

EXPOSE 22

USER root

ENTRYPOINT service ssh start && bash
