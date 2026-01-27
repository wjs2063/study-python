
FROM fluent/fluent-bit:latest-debug

COPY conf/fluent-bit.conf /fluent-bit/etc/fluent-bit.conf
COPY conf/parsers.conf    /fluent-bit/etc/parsers.conf

CMD ["/fluent-bit/bin/fluent-bit", "-c", "/fluent-bit/etc/fluent-bit.conf"]
