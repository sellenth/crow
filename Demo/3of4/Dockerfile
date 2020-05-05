FROM ubuntu:18.04

#Install and configure nesecary tools
RUN apt update 
RUN apt -y upgrade 
RUN apt install -y openssh-server python3-pip tmux git netcat --fix-missing
RUN apt -y install curl dirmngr apt-transport-https lsb-release ca-certificates
RUN curl -sL https://deb.nodesource.com/setup_12.x | bash -
RUN apt install -y nodejs
RUN mkdir /var/run/sshd
RUN sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed -i 's/#PermitRootLogin yes/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd
RUN pip3 install qrcode SpeechRecognition pillow shamir
RUN npm install fs qrcode-reader jimp net crypto-js
EXPOSE 22 3001
#Change root password
RUN echo "root:crow" | chpasswd


#Copy nesecary files
RUN mkdir app
COPY crow /app/crow
WORKDIR "/app/crow"
RUN rm -rf shamir/assets
COPY crow/Demo/3of4/assets shamir/assets
COPY crow/Demo/3of4/settings.py shamir/code/settings.py

#Set up user directory
RUN echo cd /app/crow/shamir/code >> /root/.bashrc

#Change setting file to reflect node ID
ARG ID
RUN sed -i "s/'auth'/'$ID'/" /app/crow/shamir/code/settings.py

#Start ssh server
CMD ["/usr/sbin/sshd", "-D"]
