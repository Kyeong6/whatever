# 업무내용

- 스크립트 연결 및 예외처리 진행

## 8/26

### 야간 유량 데이터 저장

해당 기능은 10분을 주기로 실행해야한다. 이전 9분 데이터와 현재 10분 정각의 데이터를 반영하여 평균 값을 NIGHT_FLOW_VAL_TB 테이블에 적재해야하는데 여기서 문제가 존재한다.

이전 9분 데이터는 조회를 하면 되기 때문에 문제가 없지만, 현재 시간의 데이터를 반영할 수 있나?라는 문제가 있다.

이를 해결하기 위해서 최근데이터 **검증** 로직을 추가했다.

추가한 함수는 다음과 같다.

```python
def is_latest_data_included(self):
        # 최신 데이터 포함 확인
        latest_time = datetime.now().replace(second=0, microsecond=0)
        # 이전 9분의 시작 시간
        start_time = latest_time - timedelta(minutes=9) 
        # 현재 시간
        end_time = latest_time 

        # 데이터 수집이 start_time ~ end_time까지 완료 여부 확인
        night_data = read_night_flow_values(end_time, minutes=9)
        if night_data:
            # 데이터 수집 시간들이 모두 9분 이내에 있는지 확인
            data_times = [datetime.strptime(d['time'], '%Y-%m-%d %H:%M:%S') for d in night_data]
            return all(start_time <= dt <= end_time for dt in data_times)
        return False
```

해당 함수를 사용하면 필요한 데이터가 모두 수집되었는지 확인할 수 있다.

이후 스케줄링 스크립트에서 `is_latest_data_included` 를 먼저 실행하여 데이터 포함 여부를 확인하고 이후 로직을 수행한다. 

기존에 야간 유량 시간대를 확인하는 로직을 구현했지만, APScheduler로 해당 시간대에 주기적(`cron`)으로 실행하는 로직을 변경했다. 

### 서버용 데이터 전송: 파일 기반 큐잉 시스템

해당 기능은 10분을 주기로 텍스트 데이터를 전송한다. 1분 주기인 이상치 데이터를 그대로 사용하면서 예측관련 값은 모두 0이었다가, 1시와 같은 정각일 경우에 예측값이 존재하기 때문에 1시간 주기인 예측 기능과도 밀접한 관련이 있다. 

**고려사항**

- serial 통신을 이용한 수신을 진행할 때 DB에 없는 센서ID도 포함되었기 때문에 DB 조회 후 전송은 배제
- `중간 매개체로 txt 파일 사용하여 10분 데이터(10 rows) 전송 후 파일 리셋`
  
<br/>

<img width="957" alt="스크린샷 2024-08-26 오후 3 53 05" src="https://github.com/user-attachments/assets/453b9912-9a26-47c0-9b6a-945f79cf5cf1">

<br/>

**개발 진행**

Kafka의 Kafka Cluster와 같이 큐잉 시스템 개념을 도입해서 `파일 기반 큐잉 시스템 방식` 으로 해당 기능을 진행

- server_data.txt에 값들을 저장
- 예측값:
    - 서버 데이터 전송은 10분 간격이므로, 1시간 정각이 아니면 값을 0으로 보냄
    - 정각일 경우 주기가 1시간인 LSTM 예측을 하여 얻은 flow / pressure 예측값을 concat하여 sensor_data.csv에 넣은 값을 조회하여 전송
- server_data.txt가 Kafka Cluster와 같은 역할을 하여 큐잉 시스템을 사용했다.
- 큐잉 시스템에서 데이터의 무결성을 유지하기 위해 `import threading import Lock` 을 사용하여 server_data.txt를 구성할 때 Lock을 걸어 다른 스레드가 해당 파일을 접근하지 못하게 방지