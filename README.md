# 🎈 Streamlit 쇼케이스

파이썬 스크립트만으로 만든 데이터 웹앱 10가지 예시입니다. HTML·CSS·자바스크립트를 직접 작성하지 않고, `streamlit` 함수 호출만으로 화면을 구성합니다. 홈 페이지 하나에 10개의 데모를 사이드바 메뉴로 묶었습니다.

## 데모 10선

| # | 데모 | 보여주는 강점 |
|---|------|--------------|
| ① | 매출 대시보드 | 사이드바 필터 · KPI · 인터랙티브 차트 · CSV 다운로드 |
| ② | 데이터 탐색기 | 화면에서 직접 편집하는 표 · 정렬 · 검색 |
| ③ | 챗봇 | 채팅 UI · 대화 기록 유지 · 스트리밍 출력 |
| ④ | 예측 시뮬레이터 | 슬라이더 조작 즉시 재계산되는 반응형 UI |
| ⑤ | 환율 대시보드 | 외부 API 실시간 조회 · 캐시 · 예외 처리 |
| ⑥ | 이미지 편집기 | 파일 업로드 · 이미지 가공 · 결과 다운로드 |
| ⑦ | 설문 폼 | 입력 묶음 제출 · 응답 누적 · 집계 |
| ⑧ | 지도 시각화 | 위경도만으로 지도 표시 |
| ⑨ | 텍스트 분석기 | 실시간 텍스트 통계 · 빈출 단어 |
| ⑩ | ROI 계산기 | 재무 계산 · 손익분기 그래프 |

## 로컬에서 실행

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

브라우저에서 `http://localhost:8501` 이 자동으로 열립니다.

## 검증

```bash
python test_pages.py
```

Streamlit 공식 테스트 프레임워크(AppTest)로 11개 페이지를 헤드리스 실행해 예외가 없는지 확인합니다.

## 배포 (Streamlit Community Cloud)

1. 이 저장소를 GitHub에 올립니다.
2. [share.streamlit.io](https://share.streamlit.io) 에 GitHub 계정으로 로그인합니다.
3. **New app → 이 저장소 선택 → Main file path 를 `streamlit_app.py` 로 지정 → Deploy** 를 누릅니다.
4. 이후 코드를 push 하면 자동으로 다시 배포됩니다.

## 폴더 구조

```
streamlit-showcase/
├── streamlit_app.py       # 진입점: st.navigation 으로 페이지 묶음
├── app_pages/             # 홈 + 데모 10개
├── utils/                 # 공용 샘플 데이터·UI 조각
├── .streamlit/config.toml # 테마(Woka 오렌지)
├── requirements.txt
└── test_pages.py          # 페이지 자동 검증
```

---

© Woka. All Rights Reserved
