FROM ubuntu:latest
LABEL authors="jeonjaehyeon"

# argument 인자를 주는게 CMD
CMD ["-b","hello world"]

# 실행할 명령어를 지정하는게 ENTRY POINT
ENTRYPOINT ["echo"]

# 즉 실행할 명령어 혹은 프로그램은 ENTRY POINT, 덮어쓰려면 docker run --entrypoint echo 등으로 변경, 마지막값만 적용됨

# 명령어 인자를 전달하려면 CMD 로 전달