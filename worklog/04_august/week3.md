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