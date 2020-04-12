FROM ubuntu:19.04


RUN apt update
RUN apt -y upgrade
RUN apt install -y openssh-server python3-pip tmux git netcat vim
RUN mkdir /var/run/sshd

RUN sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed -i 's/#PermitRootLogin yes/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN echo "root:crow" | chpasswd
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd
EXPOSE 22

ARG ID

RUN pip3 install shamir
RUN mkdir app
COPY crow /app/crow
RUN rm -rf /app/crow/shamir/assets
COPY crow/Demo/3of4/assets /app/crow/shamir/assets
COPY crow/Demo/3of4/settings.py /app/crow/shamir/code
RUN echo cd /app/crow/shamir/code >> /root/.bashrc
WORKDIR "/app/crow"
RUN echo $ID
RUN sed -i "s/'auth'/'$ID'/" /app/crow/shamir/code/settings.py

CMD ["/usr/sbin/sshd", "-D"]
