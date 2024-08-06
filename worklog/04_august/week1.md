# 업무내용

- 개발 진행하면서 내용 정리

## 8/5

### 개발 진행 정리

**SQLite GUI**

- SQLite를 관리하기 위한 GUI 설치 : "DB Browser for SQLite"
- 사용법 : [DB Browswer for SQLite](https://seong6496.tistory.com/233)

**테스트**  

테스트 진행을 위한 스크립트는 다음과 같다.
- tests/test_insert_sensor_data.py
- tests/test_lstm_process.py

테스트를 위해 두 스크립트 생성하고 실행하여 기능이 잘 구현됨을 확인했다.

**Database Lock?**

기능 구현 테스트를 진행한 후 최종적으로 SQLite GUI로 Table을 확인하여 문제가 없음을 파악했다. 

다시 테스트를 진행하기 위해서 예측값이 존재하는 PRED_VAL_TB의 행(데이터)을 SQL문을 통하여 삭제했는데 다음과 같은 오류가 발생했다.

```bash
Traceback (most recent call last):
  File "/Users/kyeong6/Desktop/github_submit/WVR/tests/test_insert_sensor_data.py", line 31, in <module>
    test_insert_sensor_data()
  File "/Users/kyeong6/Desktop/github_submit/WVR/tests/test_insert_sensor_data.py", line 18, in test_insert_sensor_data
    transformer.load_sensor_data_to_db()
  File "/Users/kyeong6/Desktop/github_submit/WVR/src/transform.py", line 44, in load_sensor_data_to_db
    insert_real_value(datetime_obj, flow_rate, pressure)
  File "/Users/kyeong6/Desktop/github_submit/WVR/db/crud.py", line 57, in insert_real_value
    db.execute("""
  File "/Users/kyeong6/Desktop/github_submit/WVR/db/database.py", line 31, in execute
    cursor.execute(query, params)
sqlite3.OperationalError: database is locked
```

해당 오류는 `database is locked` , 데이터베이스가 Lock 상태가 되었다는 것이다. 

**그럼 왜 데이터베이스가 Lock 상태가 된 것일까?**

Lock 상태라는 것은 결국 여러 트랜잭션이 동시에 데이터베이스에 접근할 때 발생하는 것이다. 

SQLite는 파일 기반 데이터베이스이기 때문에 한 번에 하나의 프로세스만 쓰기(Write) 접근이 가능하다. 

내가 SQLite GUI를 통해 SQL문을 실행한 것이 트랜잭션이 발생한 것이고 이때 SQLite GUI에서 DB를 `disconnect`, `close` 하지 않았기 때문에 `tests/test_lstm_process.py` 스크립트를 수행하면 2개의 트랜잭션이 데이터베이스에 접근하는 것이기 때문에 Lock 상태가 된 것이다. 

참고로 단순히 테이블을 확인하는 것은 문제가 없고, 쓰기 작업(SQL문 작성 후 실행)을 할 경우 문제가 된다. 

<img width="1251" alt="스크린샷 2024-08-05 오후 4 14 20" src="https://github.com/user-attachments/assets/a65383c6-bb50-48e6-802b-ce2d8139ab76">


만약 GUI에서 SQL문을 수행해야하는 상황이라면 SQL문을 실행한 후 이미지 오른쪽에 `Close Database` 를 누르자!

테스트를 진행하는 동안에는 스크립트 실행에서의 데이터베이스 Lock 상태는 발생하지 않았지만, 만약 발생할 경우에도 트러블 슈팅을 작성하도록 해야겠다.


**Flow rate / Pressure 나눠서 생각하기**

현재 Flow rate(유량)과 Pressure(수압력)을 같은 파라미터와 스케일러(.h5, .pkl)로 예측하고 있다. 

여기서 문제점은 두 개의 예측 성능이 다르다는 것이다. 현재 사용하고 있는 파라미터와 스케일러는 수압력에는 좋은 예측 성능을 보이지만 유량에서는 정규화가 잘 못 되어있는지 그래프 모양은 비슷하지만 높이차가 존재한다. 결국 예측을 할 때 다른 파라미터와 스케일러를 도입해야하기 때문에 output/Learning_lstm 디렉토리 내에 파일명을 다르게 해서 예측을 수행해야 한다. 

이후에 1년에 한 번씩 센서를 통해 얻은 실제값을 통해 모델을 재학습을 해야하기 때문에 재학습 결과를 해당 디렉토리에 동일한 파일명으로 저장을 수행해야한다. 

정리하자면 다음과 같다.

- output/Learning_lstm 디렉토리에 유량 / 수압력에 맞는 파라미터, 스케일러 구분해서 저장 후 예측 기능 수행 시 해당 파일명을 참조
- 1년에 한 번씩 모델을 재학습을 할 때 학습 결과물을 output/Learning_lstm에 동일한 파일명으로 위치

<br/></br>
**아키텍처에 따른 기능 구현 정리**

최종적으로 위에서 유량과 수압력 예측까지 나눠서 아키텍처에 따른 기능을 정리하고 프로젝트를 진행하려고 한다. 

- crud 스크립트
    - 테이블 생성 : 가장 처음 수행되어야 하는 기능 → 테이블 생성 클래스
    - 실제값 적재 : 테이블 생성 후 수행 → 이상치 검출과 같이 1 min이므로 이상치 검출 클래스
    - 유량  / 수압력 예측을 위한 조회 : REAL_VAL_TB 조회(60 min) → 예측 클래스 (1)
    - 예측값 적재 : LSTM 예측 후 수행 → 예측 클래스 (2)
    - 예측값 갱신 : LSTM 예측 후 수행 → 예측 클래스 (2)

- 예측 스크립트
    - LstmPredictionProcessor 클래스에 함수 포함
        - 유량 / 압력 예측을 위한 조회 : 해당 crud 함수를 사용한 후 데이터프레임 생성 (1)
        - 데이터프레임 위치 : 생성된 데이터프레임을 input 디렉토리에 위치 (2)
        - 예측 수행 : 유량 / 수압력 예측 진행 후 데이터 저장 및 txt 변환 (3)

**유량 / 수압력을 예측을 수행할 때 나눠서 진행해야하므로 src/lstm 디렉토리에 존재하는 파일들 수정 필요!**