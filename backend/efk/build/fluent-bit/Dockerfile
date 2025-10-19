# ✅ 공식 Fluent Bit 이미지 기반 (최신 안정 버전)
FROM fluent/fluent-bit:latest

# ✅ 설정 파일 복사 (conf 디렉터리에서 가져온다고 가정)
COPY conf/fluent-bit.conf /fluent-bit/etc/fluent-bit.conf
COPY conf/parsers.conf    /fluent-bit/etc/parsers.conf

# ✅ 실행 명령 (compose에서 command 생략 가능)
CMD ["/fluent-bit/bin/fluent-bit", "-c", "/fluent-bit/etc/fluent-bit.conf"]
