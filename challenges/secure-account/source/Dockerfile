FROM alpine:latest

RUN apk add --update --no-cache socat python3 dropbear

COPY pwdgen/pwdgen.py /usr/local/bin/pwdgen.py
RUN chmod a=rx,u+w /usr/local/bin/pwdgen.py
COPY pwdgen/pwdgen-daemon.py /usr/local/sbin/pwdgen-daemon.py
RUN chmod a=r,u+wx /usr/local/sbin/pwdgen-daemon.py

COPY start.sh /start.sh
RUN chmod a=r,u+wx /start.sh

RUN chmod +s /bin/busybox

EXPOSE 22

ENTRYPOINT [ "/start.sh" ]
