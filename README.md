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
|July|3rd|[파이프라인 개발](https://github.com/Kyeong6/whatever/blob/main/worklog/03_july/week3.md)|

<br/></br>


## LSTM 파이프라인


![LSTM_pipeline_db](https://github.com/Kyeong6/whatever/assets/100195725/4e680ad7-d452-43a7-b1be-a21ddbf6ed7c)
</br></br>
### **데이터베이스 테이블 구조**

| time | flow_rate  | pressure | flow_rate_predict | pressure_predict |
| --- | --- | --- | --- | --- |
| 2024-07-09 0:00 | 224 | 45 | 222 | 43 |
| 2024-07-09 0:01 | 227 | 36 | 225 | 34 |
- flow_rate : 순시유량
- pressure : 압력

</br></br>
### **기능 별 플로우**

**예측값 확인**

| No. | Work | Description |
| --- | --- | --- |
| 1 | 목업 데이터 사용 | Sensor를 통해 얻은 데이터를 대신해 csv 파일에 목업데이터를 설정해 개발 진행 |
| 2 | 데이터 적재 | 목업데이터를 SQLite3에 적재하는 과정 수행 |
| 3 | CSV 파일 변환 | 특정 시간에 1일(0~24시) 데이터를 조회하여 csv 파일로 변환한 후 LSTM 파이프라인 내에 존재하는 Input 디렉토리에 위치 |
| 4 | 데이터 형식 변환 | csv 파일에 존재하는 데이터를 Prediction.py를 실행할 수 있게 데이터 형식 변환<br>timestamp : datetime<br>value : float |
| 5 | 예측 수행 | LSTM 모델을 통한 예측 수행 후 예측값 저장(csv 파일) : Output/Prediction/prediction.csv<br>예측 방법 : 1일 1분신 정책으로 인한 ID+1H 방식 반영(i = 1 ~ 6) |
| 6 | 예측값 전송 | 1분 ~ 60분으로 총 6개의 파일에 24개의 행이 존재한다.<br>1일 1회 CSV(파일명: Day{step}prediction.csv) 파일을 서버로 전송<br>전송 방식 : requests 라이브러리 사용<br>(전송 방식은 요청방식에 따라 JSON 형식으로 변환 후 전송할 수 있음)<br>전송한 후 파일은 리셋을 진행한다. |
| 7 | 예측값 저장 | 예측값을 데이터베이스에 저장 |
| 8 | 스케줄러 도입 | 위 과정을 설정한 주기에 따라 백그라운드 실행 |

</br></br>

**이상치 확인**

| No. | Work | Description |
| --- | --- | --- |
| 1 | 목업 데이터 사용 | Sensor를 통해 얻은 데이터를 대신해 csv 파일에 목업데이터를 설정해 개발 진행 |
| 2 | DB 적재 | 목업데이터를 SQLite3에 적재하는 과정 수행 |
| 3 | DB 조회 | 1분마다 DB를 조회하여 해당 값 이상치 유무 판단 진행을 위한 준비 |
| 4 | 이상치 확인 | 이상치 파악 방법 : 정규분포 사용하여 단계(변수) 설정<br>0단계 : 정상<br>1단계 관심 : 90 ≤ value ≤ 95<br>2단계 주의 : 95 ≤ value < 98<br>3단계 경계 : 98 ≤ value < 99<br>4단계 심각 : 99 ≤ value ≤ 100 |
| 5 | 알림 | 이상치일 경우 JSON 파일 형식으로 전달<br>{<br>”sensor_id” : "sensor_01"<br>”time” : "2024-07-09 0:01",<br>”outlier_stage” : 3,<br>”value” : 227<br>}<br>(machine_number 같은 경우 중앙 서버에서 구별할 수 있으면 제거) |
| 6 | 스케줄러 도입 | 위 과정을 설정한 주기에 따라 백그라운드 실행 |
