FROM python:alpine

# Set the name of the image
LABEL image.name="cargodeck"

# Set the working directory inside the container
WORKDIR /usr/src/app
VOLUME /usr/src/app

# Copy the CargoDeck.py and related folders with contents
COPY Loader.py ./
COPY CargoDeck.py .
COPY static static
COPY templates templates

# Install dependencies needed.
RUN apk update 
RUN apk add openssl		# Address known vulnerability in the current python:alpine image

# Install Flask and any other necessary Python dependencies
RUN pip install flask
RUN pip install docker
RUN pip install gunicorn
RUN pip install gevent

# Expose the port
EXPOSE $LOGLEVEL
EXPOSE $PORT
EXPOSE $MATCH
EXPOSE $WORKERS
EXPOSE $CARGODECK_VERSION

# Set defaults.
ENV LOGLEVEL=INFO
ENV PORT=80
ENV MATCH=CargoDeck
ENV WORKERS=1
ENV CARGODECK_VERSION=1.0.0

# Create /tmp/startup.sh script:
#    * Outputs CARGODECK_VERSION to the log.
#    * Execute Loader.py, which in turn start the (multiple?) instance of Gunicorn.
# BEWARE: This Dockerfile must be saved as a Unix file, with LF line-endings, or the scripts below will fail!

RUN cat > /tmp/startup.sh <<EOF
#!/bin/sh -u
echo "[\$(date '+%Y-%m-%d %H:%M:%S +0000')] [$$] [INFO] CargoDeck version \$CARGODECK_VERSION"

sleep 0.5
exec python Loader.py
EOF

RUN chmod +x /tmp/startup.sh

CMD ["sh", "/tmp/startup.sh"]
