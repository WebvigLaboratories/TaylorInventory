# Dockerfile

# FROM directive instructing base image to build upon
FROM python:2-onbuild

# COPY startup script into known file location in container
COPY start.sh /start.sh

# EXPOSE port 30600 to allow communication to/from server
EXPOSE 30600

#WORKDIR WebvigLabs

ENV DATABASE_URL postgres://flbiqwiy:nVFtiJDttMb8zcJd1Cyo-ioq2yTW1k3h@pellefant.db.elephantsql.com:5432/flbiqwiy

# CMD specifcies the command to execute to start the server running.
CMD ["/start.sh"]
