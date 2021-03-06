FROM lsiobase/alpine.python:3.7

# set version label
ARG BUILD_DATE
ARG VERSION
LABEL build_version="T version:- ${VERSION} Build-date:- ${BUILD_DATE}"
LABEL maintainer="T"

RUN \
echo "**** install app ****" && \
git clone --depth=1 https://github.com/purplederple/CaptureBate /app/cb && \

echo "**** install packages ****" && \
cd /app/cb && pip install --no-cache-dir -r requirements.txt \

# copy local files
COPY root/ /
COPY config/ /

# ports and volumes
VOLUME /config /data
