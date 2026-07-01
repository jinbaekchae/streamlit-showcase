"""AppTest 로 모든 페이지를 헤드리스 실행해 예외가 없는지 검증한다."""

import sys

from streamlit.testing.v1 import AppTest

PAGES = [
    "app_pages/home.py",
    "app_pages/dashboard.py",
    "app_pages/explorer.py",
    "app_pages/chatbot.py",
    "app_pages/predictor.py",
    "app_pages/fx.py",
    "app_pages/image_lab.py",
    "app_pages/survey.py",
    "app_pages/map_view.py",
    "app_pages/text_analyzer.py",
    "app_pages/roi.py",
]

failed = 0
for path in PAGES:
    try:
        at = AppTest.from_file(path, default_timeout=60)
        at.run()
        if at.exception:
            failed += 1
            print(f"[FAIL] {path}")
            for e in at.exception:
                print("       ", e.value)
        else:
            print(f"[ OK ] {path}")
    except Exception as exc:  # noqa: BLE001
        failed += 1
        print(f"[ERR ] {path}: {type(exc).__name__}: {exc}")

print("=" * 40)
print(f"통과 {len(PAGES) - failed} / {len(PAGES)}")
sys.exit(1 if failed else 0)
