FROM fluent/fluentd:v1.19.0-debian-arm64-2.1
USER root

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential ruby-dev ca-certificates \
 && update-ca-certificates

RUN gem install --no-document fluent-plugin-mongo -v 1.6.0 \
 && mkdir -p /fluentd/etc /fluentd/fluentd-buffer \
 && chown -R fluent:fluent /fluentd
USER fluent
