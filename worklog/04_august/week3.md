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

### 이상치 코드 리팩토링

예측 기능은 완료가 되었지만, 이상치 코드를 디렉토리 구조에 맞게 리팩토링을 진행해야한다. 이상치 코드 리팩토링이 끝난 후 동시성 및 주기 작업 코드를 진행할 예정이다.