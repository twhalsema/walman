vagrant up walmandbserver

vagrant ssh walmandbserver -c  "echo 'vagrant' | sudo -S sleep 1 && sudo sh -c \"echo 'vagrant ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/vagrant\" && sudo -S hostnamectl set-hostname walmandbserver.example.com && sudo -S dnf -y install python3.12"

vagrant up walmandbclient1

vagrant ssh walmandbclient1 -c  "echo 'vagrant' | sudo -S sleep 1 && sudo sh -c \"echo 'vagrant ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/vagrant\" && sudo -S hostnamectl set-hostname walmandbclient1.example.com && sudo -S dnf -y install python3.12"

vagrant up walmandbclient2

vagrant ssh walmandbclient2 -c  "echo 'vagrant' | sudo -S sleep 1 && sudo sh -c \"echo 'vagrant ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/vagrant\" && sudo -S hostnamectl set-hostname walmandbclient2.example.com && sudo -S dnf -y install python3.12"
