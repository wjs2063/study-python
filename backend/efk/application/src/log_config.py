import logging
import logging.config
from pythonjsonlogger import jsonlogger
import datetime
import pytz  # pip install pytz


class KSTISOFormatter(jsonlogger.JsonFormatter):
    def formatTime(self, record, datefmt=None):
        kst = pytz.timezone("Asia/Seoul")
        dt = datetime.datetime.fromtimestamp(record.created, tz=kst)
        return dt.isoformat()  # ISO 8601 형식 (예: 2025-01-11T10:30:00+09:00)


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": KSTISOFormatter,  # ← 위에서 정의한 formatter 사용
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",  # KST 포맷
        }
    },
    "handlers": {
        # ✅ 정상 로그는 stdout
        "stdout": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",  # 👈 추가!
            "formatter": "json",
        },
        # ⚠️ 에러 로그는 stderr (선택적으로 분리)
        "stderr": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
            "formatter": "json",
        },
    },
    "loggers": {
        # 앱 로거: stdout
        "efk_app": {
            "handlers": ["stdout"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.error": {     # ✅ Uvicorn 서버 로거
            "handlers": [],    # 보내지 않음
            "level": "WARNING",  # INFO 로그 차단
            "propagate": False
        },
        "uvicorn.access": {    # 접근 로그도 확실히 끄고 싶으면
            "handlers": [],
            "level": "WARNING",
            "propagate": False
        },
    },
    "root": {
        "handlers": ["stdout"],  # root까지 stdout
        "level": "INFO",
    }
}


def get_logger(name):
    logging.config.dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger(name)
    return logger


log = get_logger("efk_app")
