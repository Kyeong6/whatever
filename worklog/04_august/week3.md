# 업무내용

- 기능 실행시간 파악
- 다른 인원이 작성한 이상치 코드 리팩토링

## 8/19

### 기능 실행시간 파악

**학습(9개월 데이터 기준, 12개월일 경우 52만행)**

- 데이터 전처리 : 33 sec
- 모델 학습(유량 / 수압력) : 121085 sec(약 34시간)

**예측 파이프라인**

현재 LSTM 파이프라인을 학습 → 예측까지 진행이 잘 되고있음을 확인했다.(tests/test_pred_pipeline.py)

```bash
# 명령어  
Starting Flow Rate Training
Running flow rate preprocessing
Running flow rate model training
Flow Rate training completed.
Flow Rate Training Completed
Starting Pressure Training
Running pressure preprocessing
Running pressure model training
Pressure training completed.
Pressure Training Completed
Starting LSTM Prediction
Start process_prediction
flow prediction finish
pressure prediction finish
 6.0738 sec
cpu usage               : 0.0 %
memory usage            : 0.04 GB
Finish process_prediction
001  231102  231102  02  8.02  4.11
001  231103  231103  02  8.05  4.11
001  231104  231104  02  8.07  4.11
001  231105  231105  02  8.08  4.11
001  231106  231106  02  8.09  4.11
001  231107  231107  02  8.11  4.12
001  231108  231108  02  8.12  4.12

LSTM Prediction Completed
 257.6708 sec
cpu usage               : 1.2 %
memory usage            : 0.04 GB
```

테스트를 진행하기 위해서 학습 데이터를 500개만 사용하여 진행했다. 

## 8/20

### 추후 프로젝트 진행 순서

1. 이상치 코드 리팩토링
    - 예측 기능은 완료 이후 이상치 코드를 프로젝트 디렉토리 구조에 맞게 리팩토링 진행 필요
2. Pyserial을 이용한 Serial 통신
    - 통신 프로토콜에 맞는 텍스트 데이터(ASCII) 읽기 작업
    - 1분 주기인 이상치 값, 10분 주기인 예측값 구성 후 반환 작업
        - 추가적으로 센서 ID를 반환할 때 1분 데이터로 받은 센서 ID 반환 작업 필요
3. 스케줄러 도입
    - 기능 별 주기 설정
4. 동시성(비동기 및 멀티 프로세싱) 도입
    - 스케줄러 작업에 대한 동시성 개념 도입
5. 예외처리 진행
    - 센서 데이터를 못 받았을 경우에 대한 예외처리 필요
    - 이후 데이터가 없을 경우의 기능에 대한 예외처리 필요

### 이상치 코드 리팩토링 진행

**이상치 기능 코드**

- build_criteria.py:
    - 특정 파일(DB, initial_data.txt)들을 읽어 분석한 기준치를 저장하는 코드
    - 현재, 텍스트 파일의 모든 줄을 돌며 수행하기 때문에 반복문의 역할 수행
    - 나중의 반복성을 제거하기에 가장 적합하여, 해당 파일에 반복 코드 넣음
- outlier_detection.py:
    - process_data.py로부터 이상치 검출을 요청받는 코드
    - 해당 스크립트에 외부로 결과를 내보내는 alert() 함수 존재
        - 해당 함수는 기준치를 읽어오지 않지만, 인자로써 기준치를 저장하는 코드
- process_data.py:
    - 이상치 검출 플로우의 시작 코드
    - 기존에 main.py에 있던 함수들을 모아놓은 코드
- main.py
    - 각종 파일 위치 작성된 코드

**질문사항(코드 작성한 팀원)**

```python
# DB에 야간 데이터 테이블 생성 함수
def create_night_val_table(conn):
    # 22:00 ~ 04:50의 10분 단위 컬럼 생성
    columns = ', '.join([f'"{h:02}:{m:02}" REAL' for h in range(22, 24) for m in range(0, 60, 10)])
    columns += ', ' + ', '.join([f'"{h:02}:{m:02}" REAL' for h in range(0, 5) for m in range(0, 60, 10)])

    # 테이블 생성 쿼리 실행
    query = f'''
    CREATE TABLE IF NOT EXISTS night_VAL_TB (
        Timestamp TEXT PRIMARY KEY,
        {columns}
    )
    '''
    conn.execute(query)
    conn.commit()
```

- 야간 데이터 테이블을 생성은 어떤 용도인지?
    - 답변 : 3개월에 한 번씩 야간 유량 시간대를 파악하기 위한 야간 시간대(22시 ~ 05시)에만 해당하는 10분 데이터의 평균값을 넣는 테이블
- 테이블을 생성만 하고 추가적인 crud 작업이 왜 없는지?
    - 답변 : crud.py에 넣어야하지만 DI(의존성 주입)이 어려워 process_data.py에 위치시킴

**이상치 기능 추가로 인한 주기 수정**

이상치 기능에서의 주기는 다음과 같다.

- 1분 : 수집된 센서 데이터를 기반으로 이상치 검출
- 10분 : 야간 시간대의 유량 데이터 10개의 평균값을 DB에 저장
- 3개월 : 기준(criteria) 재설정

**수행 과정**

현재 제공받은 이상치 코드가 의존성 주입(DI)이 되어있지 않고, 중복요소들이 존재하여 전반적인 수정이 필요하다.

1. 야간 유량 테이블을 crud.py에서 테이블 생성 함수로 넣기
    - 서버 실행 후 바로 존재해야하기 때문
2. process_data.py에 존재하는 store_night_data 함수는 crud.py로 이전
    - 해당 작업은 CRUD 작업인데 실행 파일에 존재하기 때문에 이전 후 모듈로 불러와서 사용
3. 현재 스크립트인 build_criteria.py, outlier_detection.py, process_data.py에서 process_data.py의 코드는 다른 두 스크립트로 합치기
    - 굳이 하나의 파일로 나눌 이유 x → class로 묶을 수 있기 때문
4. 최종적으로 도메인(클래스) 별로 나누기
    - 이상치 검출 : 유량 / 수압력
    - 이상치 기준 : 초기 세팅 / 3개월 이후 세팅
    - 이상치 검출 방식 : 4가지 존재(유량은 4가지 모두 적용, 수압력은 3가지 적용)
    - 이상치 기준을 세우기 위한 10분의 평균값 저장
- 정리:
    - outlier_detection.py
        - 도메인에 따른 이상치 검출 유량 / 수압력 각각 클래스 생성(test에서는 해당 클래스 2개를 사용)
        - 이상치 관련 스크립트를 모듈로 불러와서 사용하는 이상치 검출 수행 스크립트
    - outlier_method.py
        - 이상치 검출 방식 클래스를 생성하여 이상치 검출 방식 4가지 방식을 메서드로 구현
    - build_criteria.py
        - 이상치 기준을 함수로 구현한 후 유량 클래스(outlier_detection.py)에서 조건문을 사용하여 초기에만 initial_data.txt 사용하는 야간 유량 기준 수행
    - night_flow_value.py
        - 10분 간의 데이터를 이용하여 평균값 DB 적재


## 8/21

### 이상치 코드 리팩토링 진행

build_criteria.py(기준 정의)와 outlier_method.py(이상치 검출 방식 정의)간의 연결하는 작업에 어려움을 겪고있어 아키텍처부터 다시 파악하며 구현을 진행

![image.png](https://github.com/user-attachments/assets/8b2574c1-94f5-4a36-8728-7ca5573663fd)

1. 이상치 기준 정의(build_criteria.py)

이상치 검출을 위해서는 사전에 기준 정의가 필요하다. build_criteria.py의 서버가 실행되고 이상치 관련 코드 중 처음으로 작동되어야하는 건 CriteriaBuilder 클래스 내부의 메서드

2. 이상치 검출 방식(outlier_method.py)

기준 정의 내용이 존재하는 txt 파일에서 각 이상치 검출 방식에 사용되는 요소를 추출(CriteriaBuilder의 load_criteria_from_txt 메서드 활용)하여 적용

현재 이상치 검출 관리 클래스(AnomalyDetector)를 이용하여 최종적인 이상치 관리를 수행하려 했지만, 도메인에 따른 이상치 진행 파일(outlier_detection.py)로 이전

3. 도메인에 따른 이상치 검출 진행(outlier_detection.py)

도메인(유량 / 수압력)에 따라서 각각 클래스를 사용하여 최종적인 이상치 검출을 진행한다. 이상치 검출 방식 스크립트(outlier_method.py)에 존재하던 이상치 검출 관리 클래스(AnomalyDetector) 내용과 전반적인 검출 내용을 도메인에 맞게 구성한 후 스케줄링 스크립트에 클래스를 포함시켜 기능 구현 완료

4. 야간 유량 데이터 저장

이상치 기준을 정의할 때 서버를 실행하고 초기에는 실측값이 없어 미리 세팅해놓은 txt 파일을 이용하여 기준을 정의

3개월이 지난 시점부터는 DB에 적재된 내용을 기반으로 기준을 정의하므로 야간 유량 10분 데이터의 평균값을 DB(NIGHT_FLOW_VAL_TB)에 적재


## 8/22

### Serial 통신을 이용한 센서 데이터 수집 로직 수행

데이터 수집(SensorReceiver) 및 송신(SensorTransmitter) 클래스 내부에 메서드를 생성하여 Serial 통신을 진행한다.

**SensorReceiver**

- 시리얼 통신을 통한 데이터 수신(read_data)
- 데이터 파싱(parse_sensor_data)
- 데이터베이스에 적재(load_sensor_data_to_db)
- 전체 실행 로직(receiver)

**SensorTransmitter**

- 알림 데이터 송신(send_alert)
- 서버 데이터 송신(send_server)
- 전체 실행 로직(transmit)

Serial 통신까지 어느 정도 구현이 되어서 남은 부분은 다음과 같다.

1. 스크립트 간의 연결 + 스케줄링 도입
2. 동시성 개념 도입
3. 예외처리

### 스크립트 간의 연결

스크립트 간의 연결짓는 작업을 수행하기 위해서는 작업 주기별 정리가 필요하다.

- 1 min : 알림용
    - 센서 데이터 수집 → 실측값 테이블 적재 → 이상치 검출 → 검출 결과 DB 적재 → 알림 / 서버용 txt 파일 구성(data/sensor/alert.txt, data/sensor/server.txt)
    - 서버 실행 후 1년이 지날 경우 데이터 삭제(해당 시간 - 365 day)
- 10 min : 서버용
    - 1 min 작업에서 서버용 텍스트 파일을 분마다 구성하고 있고, 만약 1 hr 작업이 수행된다면 예측 속성에 값 넣기(정각이 아닌 경우는 예측 속성 값 NULL)
- 1 hr : 예측용
    - 실측값 테이블 조회(60 rows) → csv 변환 수행(input) → LSTM 예측 수행 → 예측값 DB 적재 → 예측값 서버용 텍스트파일 구성
- 3 mon : 이상치 기준 설정
    - 실측값 및 야간 유량 테이블 조회 → 이상치 기준 설정 및 변경
- 1 hr : 학습용
    - 실측값 테이블 조회(1 yr) → LSTM 학습 수행(데이터 전처리 → 학습) → 모델 파일, 스케일러 파일 저장(output/Learning_lstm/flow_rate, output/Learning_lstm/pressure)


### 💡 데이터 송 / 수신


**실측 데이터 수집**

- 스크립트 : serial.py
- 단위 : 1 min
- 순서
    - 센서 데이터 수집 : SensorReceiver.read_data()
    - 데이터 파싱 : SensorReceiver.parse_sensor_data()
    - 실측 데이터 적재 : SensorReceiver.load_sensor_data_to_db()
    - 실행 : SensorReceiver.receiver()
- 설명
    - 데이터 파싱한 결과(반환값 : data)를  이상치 검출 로직에서 사용

**이상치 / 예측 데이터 송신: 알림용**

- 스크립트 : serial.py
- 단위 : 1 min
- 순서
    - 이상치 결과값 전송 : MinuteTransmitter.transmit()
- 설명
    - 이상치 검출 스크립트의 결과값들을 transmit 함수 인자로 설정

**이상치 / 예측 데이터 송신: 서버용**

- 스크립트 : serial.py
- 단위 : 10 min
- 순서
    - 이상치 / 예측 결과값 전송 :TenMinuteTransmitter.transmit()
- 설명
    - 이상치 검출 및 LSTM 예측 스크립트의 결과값들을 transmit 함수 인자로 설정
    - 예측값 같은 경우 날짜별 값을 리스트로 설정(변환 작업 포함)
- 변경사항
    - 서버용 같은 경우 텍스트파일에 저장(10 rows)한 내용을 보내기, 예측값이 존재(hr 정각)하는 제외한 경우는 0으로 설정


### 💡 이상치 검출

**이상치 기준 정의**

- 스크립트 : build_criteria.py
- 단위 : 3 month
- 순서
    - txt 파일(initial_data.txt) 조회 (초기 서버 실행) : CriteriaBuilder.load_data_from_file()
    - DB(REAL_VAL_TB) 조회(서버 실행후 3개월 이후) : CriteriaBuilder.load_data_from_db()
    - 이상치 기준 계산 : CriteriaBuilder.calculate_criteria()
    - 기준 txt 파일(flow_rate_criteria.txt / pressure_criteria.txt) 저장 : 
    CriteriaBuilder.save_criteria_as_txt()
- 실행 함수
    - 실측치 값 사용 기준 정의 : CriteriaBuilder.criteria_from_db()
    - 기본값 사용 기준 정의 : CriteriaBuilder.criteria_from_txt()
- 다른 스크립트에서 사용
    - 도메인에 맞는 criteria.txt 파일 요소 추출(딕셔너리 변환) : CriteriaBuilder.load_criteria_from_txt()
- 설명
    - 기준 정의가 이상치 검출 중 가장 먼저 실행되어 txt 파일에 저장 필요(txt 파일이 매개체)
    - 기준 정의 요소를 딕셔너리로 반환하여 이상치 검출 방법 스크립트
    (outlier_method.py / NightOutlierDetection)에서 사용

**이상치 검출 방식 정의**

- 스크립트 : outlier_method.py
- 단위 : 1 min
- 순서
    - 이상치 검출 방법론 클래스로 구분
        - 시스템 이상치 :  SystemOutlierDetection
        - 실측값 이상치 : ValueOutlierDetection
        - 예측값 이상치 : PredictOutlierDetection
        - 야간 최소 유량 이상치 : NightOutlierDetection
- 설명
    - 이상치 검출 진행 스크립트(outlier_detection.py)에서 해당 클래스를 사용

**도메인에 따른 이상치 검출 진행**

- 스크립트 : outlier_detection.py
- 단위 : 1 min
- 순서
    - 유량 이상치 진행 : FlowRateAnomalyDetector
    - 수압력 이상치 진행 : PressureAnomalyDetector
- 설명
    - 유량 / 수압력 이상치 검출 반환값을 알림용 / 서버용 전달 인자로 사용

**야간 유량 데이터 저장**

- 스크립트 : night_flow_value.py
- 단위 : 10 min
- 순서
    - 현재 시간(클래스 인자)에서 이전 9분간의 데이터를 조회하여 평균 계산 : NightFlowSaver.calculate_and_store_night_flow()
- 내용
    - 해당 스크립트는 다른 로직과의 연관성보다는 야간 유량 데이터 저장에 목적을 둠


### 💡 LSTM


**예측 진행**

- 스크립트 : lstm_processor.py
- 단위 : 1 hr
- 순서
    - 유량 / 압력 실측 데이터 조회(REAL_VAL_TB) : LstmPredictionProcessor.read_real_values_for_lstm()
    - 데이터 csv 형식 변환 : LstmPredictionProcessor.save_data_for_lstm()
    - LSTM 예측 진행 : LstmPredictionProcessor.run_lstm_prediction()
    - 예측 기능 실행 및 데이터 저장(DB / txt) : LstmPredictionProcessor.process_prediction()
    - 최종 실행 : LstmPredictionProcessor.execute()
- 설명
    - 예측 기능 실행을 한 후 예측 결과값은 서버용에 해당하므로 txt 파일 저장이 필요
    - txt 파일을 재구성(이상치 + 예측)하는 함수 추가로 구현 필요

**모델 학습**

- 스크립트 : lstm_processor.py
- 단위 : 1 yr
- 순서
    - 학습 데이터 생성(모든 REAL_VAl_TB의 유량 / 수압력 데이터 각각 조회) : LstmLearningFlowProcessor.read_all_values()
    - 데이터 csv 형식 변환 : LstmLearningFlowProcessor.save_data_for_lstm()
    - 데이터 전처리 : LstmLearningFlowProcessor.run_preprocessing()
    - 모델 학습 : LstmLearningFlowProcessor.run_training()
    - 학습 총 실행 : LstmLearningFlowProcessor.execute()


### 💡 동시성(Concurrency)

**멀티 프로세싱**

- 스크립트 : concurrency.py
- 순서
    - 유량 데이터 기반 모델 학습 : run_flow_learning()
    - 수압력 데이터 기반 모델 학습 : run_pressure_learning()
    - 멀티 프로세싱 도입 : run_multiprocessing_learning()
- 설명
    - 해당 스크립트에서 멀티 프로세싱을 적용한 후 스케줄링 스크립트(scheduling.py)에서 호출하여 사용


### 💡 스케줄링(scheduling)

**스케줄러**

- 스크립트 : scheduling.py
- 클래스 : SchedulerManager
- 순서
    - 실측 데이터 수집 및 이상치 검출 및 전송(1 min) : receive_sensor_data()
    - 서버 데이터 송신(10 min) : send_server_data()
    - 야간 유량 데이터 저장(10 min) : save_night_flow()
    - LSTM 예측 수행(1 hr) : run_lstm_prediction()
    - 이상치 기준 정의(3 month) : define_criteria()
    - 모델 학습(1 yr) : train_lstm_model()
    - 작업 스케줄링 정의 : setup_schedules()
    - 스케줄링 총 실행 : start()
- 내용
    - 스케줄링 스크립트에서는 외부 스크립트 내용을 호출하여 진행
        - 연결을 위한 인자값 설정 필요
    - 작업 스케줄링 정의 함수에서 해당 작업 함수들의 작업 관리

## 8/23

### 스크립트 간 연결작업 + 예외처리

현재 대략적인 스크립트를 모두 작성하여 최종 연결 스크립트인 `scheduling.py` 를 확인하며 다른 스크립트의 클래스, 메서드들의 예외처리를 진행한다.

**방식**

- try - except 구문을 사용하여 예외처리 진행
- except 구문이 실행될 경우 반환값을 None으로 설정하여 다음 로직에서 `if data is not None:` 과 같은 판단하는 로직 설정

### 변경사항

1. 센서 데이터 수신하는 SensorReceiver 같은 경우 1분 단위 작업으로 스케줄링하였지만, 센서 데이터는 계속 수집되어야하기 때문에 1분 단위 작업에서 제거하고 항상 돌아가는 작업으로 변경
2. 이벤트 기반 처리 방식 도입 : 콜백 호출

**실시간 데이터 수집**

해당 기능은 별도의 스레드에서 실행하게 구현했다.

- 비동기 작업 처리: 실시간 데이터 수집은 데이터가 들어오는 즉시 처리해야 하므로, 다른 주기적인 작업에 영향을 주지 않고 독립적으로 실행되어야 합니다. 별도의 스레드로 분리함으로써, 실시간 데이터 수집이 다른 작업들에 의해 방해받지 않도록 합니다. 이를 통해 데이터 수집의 지연을 최소화할 수 있다.
- CPU 사용량 관리: 실시간 데이터 수집은 계속해서 시리얼 포트를 모니터링하고 데이터를 읽어야 하기 때문에 CPU 리소스를 많이 사용할 수 있습니다. 별도의 스레드에서 이 작업을 수행하면, 메인 스레드에서는 다른 주기적인 작업들을 처리할 수 있습니다. 즉, CPU 사용량을 한 스레드에서만 집중적으로 사용하지 않고, 여러 스레드로 분산하여 사용함으로써 시스템의 전반적인 성능을 최적화할 수 있다.
    - async 같은 비동기 대신에 스레드 방식을 사용한 이유

**이벤트 기반 처리**

- 실시간 데이터 수집 로직과 실시간 데이터 기반 이상치 검출 로직을 `scheduling.py` 에서 분리 진행
- `serial.py` 의 데이터 수집 로직인 receive()를 콜백 호출을 사용한 이벤트 기반 처리를 도입
- 해당 콜백 함수는 실시간 데이터 기반 이상치 검출 로직인 handle_sensor_data()가 사용하여 로직 수행