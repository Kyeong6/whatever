# whatever
wvr 인턴에서 수행한 프로젝트를 정리하는 레포입니다. <br/></br>

## 업무 일지

|Month|week|worklog|
|------|---|---|
|May|2nd, 3rd|[LSTM 모델 분석](https://github.com/Kyeong6/whatever/blob/main/worklog/01_may/week2%2C3.md)|
|May|4th|[LSTM 모델 분석을 통해 배운 내용 정리](https://github.com/Kyeong6/whatever/blob/main/worklog/01_may/week4.md)|
|May|5th|[LSTM 모델 코드 수정 및 추가](https://github.com/Kyeong6/whatever/blob/main/worklog/01_may/week5.md)|
|June|1st|[다수의 예측값 얻기 및 시각화 진행](https://github.com/Kyeong6/whatever/blob/main/worklog/02_june/week1.md)|
|July|1st|[제품 시안을 위한 질문사항](https://github.com/Kyeong6/whatever/blob/main/worklog/03_july/week1.md)|
|July|2nd|[파이프라인 설계](https://github.com/Kyeong6/whatever/blob/main/worklog/03_july/week2.md)|

<br/></br>

## LSTM 파이프라인 

### 구조

![LSTM_pipeline](https://github.com/Kyeong6/whatever/assets/100195725/145f66f9-9e17-4526-ab47-4e3651c72f69)


### 세부사항  

**CSV 파일 구조(센서 데이터 저장)**

| time | value |
| --- | --- |
| 2024-07-09 0:00 | 224 |
| 2024-07-09 0:01 | 227 |

<br/></br>

**예측값 플로우**

| No. | Work | Description |
| --- | --- | --- |
| 1 | 목업 데이터 사용 | Sensor를 통해 얻은 데이터를 대신 csv 파일에 목업데이터를 설정해 개발 진행, 실제로는 센서의 분당 데이터 사용 |
| 2 | 데이터 조회 및 이동 | 시간 당 목업데이터를 조회하여 이전 시간의 60개의 행을 Input(LSTM 디렉토리 내에 존재하는 디렉토리)에 위치<br>Ex) 2시에 대한 예측값을 위해서는 0 ~ 1(60 rows)시의 데이터 필요 |
| 3 | 데이터 형식 변환 | csv 파일 데이터를 Prediction.py를 실행할 수 있게 데이터 형식 변환<br>timestamp : datetime<br>value : float |
| 4 | 예측 수행 | LSTM 모델을 통한 예측 수행 후 예측값 저장 : Output/Prediction/prediction.csv<br>예측 방법 : 1일 1분당 정책으로 인한 ID+반 복사 방식 (i = 1 ~ 6) |
| 5 | 예측값 저장 및 전송 | 1분 ~ 60분으로 총 6개의 파일의 24개의 행에 존재한다.<br>1일 1회 CSV(Day(step))prediction.csv 파일을 서버로 전송<br>전송 방식 : requests 라이브러리 사용<br>(전송 방식은 요청방식에 따라 JSON 형식으로 변환 후 전송할 수 있음)<br>전송한 후 파일은 리셋 진행함. |
| 6 | 스케줄러 도입 | 위 과정을 설정한 주기에 따라 백그라운드 실행 |

<br/></br>
**이상치 플로우**

| No. | Work | Description |
| --- | --- | --- |
| 1 | 목업 데이터 사용 | Sensor를 통해 얻은 데이터를 대신 csv 파일에 목업데이터를 설정해 개발 진행 |
| 2 | 참조 | 예측값은 조회한 후 csv 파일에 넣지만, 분당 데이터를 기반으로 이상치 파악을 하기 때문에 데이터를 바로 참조 진행 |
| 3 | 이상치 확인 | 이상치 파악 방법 : 정규분포 사용하여 단계(변수) 설정<br>0단계 : 정상<br>1단계 관심 : 90 ≤ value ≤ 95<br>2단계 주의 : 95 ≤ value < 98<br>3단계 경계 : 98 ≤ value < 99<br>4단계 심각 : 99 ≤ value ≤ 100 |
| 4 | 알림 | 이상치일 경우 JSON 파일 형식으로 전달(아래는 예시)<br>{<br>”machine_number” : 1<br>”time” : 2024-07-09 0:01,<br>”outlier_stage” : 3,<br>”value” : 227<br>}<br>(machine_number 같은 경우 중앙 서버에서 구별할 수 있으면 제거) |
| 5 | 스케줄러 도입 | 위 과정을 설정한 주기에 따라 백그라운드 실행 |
