# GAP R-Zone 6.5 트레이딩 대시보드

Streamlit 기반 트레이딩 대시보드입니다.

## 설치 및 실행

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 주요 기능

| 페이지 | 설명 |
|--------|------|
| 🏠 메인 대시보드 | KPI 카드, 자산 추이, 포지션 현황, 최근 매매 |
| 📊 매매 성과 | 12개 핵심 지표, 갭 범위별 성과, 결과 분포, MA 패턴/섹터별 분석 |
| 📋 매매 기록 | 전체 거래 테이블 (필터/정렬), 달력 히트맵 |
| 📡 시그널 | 활성 시그널 카드 (진행바), 볼륨 현황, 고승률 패턴 |
| 🌐 시장 개요 | KOSPI/KOSDAQ 지수, 섹터 등락률, 기관/외국인 수급, 이벤트 |
| 🛡️ 리스크 | 포지션 사이징 계산기, 비중 관리, R:R 분포, 일별 P&L |
| 💾 데이터 관리 | CSV 업로드/다운로드, 직접 입력 폼, 포지션 관리, 데이터 요약 |

## 데이터 입력 방법

1. **CSV 업로드**: 데이터 관리 > CSV 업로드 탭에서 파일 업로드
2. **직접 입력**: 데이터 관리 > 직접 입력 탭에서 폼으로 개별 매매 추가
3. **프로그래밍**: `sample_data.py`를 수정하여 기본 데이터 변경

## 파일 구조

```
streamlit-dashboard/
├── app.py            # 메인 앱 (설정, 다크 CSS, 네비게이션)
├── sample_data.py    # 샘플 데이터 (24건의 거래)
├── utils.py          # 공통 헬퍼 함수
├── requirements.txt  # 의존성
├── views/            # 페이지 모듈
│   ├── __init__.py
│   ├── overview.py
│   ├── performance.py
│   ├── trade_log.py
│   ├── signals.py
│   ├── market.py
│   ├── risk.py
│   └── data_mgmt.py
└── README.md
```
