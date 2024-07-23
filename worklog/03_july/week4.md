# 업무내용

- 파이프라인 세부사항 개발 시작

## 7/22 ~ 23

### 수행할 것

1. LSTM 모델 예측 iD+1h 개념 도입
2. 파이프라인 구축
3. LSTM 모델 1년에 한 번씩 Train 과정 수행

### LSTM 모델 예측 iD+1h 개념 도입

예측을 수행하기 위한 명령어는 다음과 같다.

```python
python 3_Prediction.py -f ./Input/pipeline_sample.csv -a
```

명령어를 실행하면 다음과 같은 오류가 발생한다.

```bash
 python 3_Prediction.py -f ./Input/pipeline_sample.csv -a
/Users/kyeong6/anaconda3/envs/lstm_pipeline/lib/python3.9/site-packages/sklearn/base.py:376: InconsistentVersionWarning: Trying to unpickle estimator MinMaxScaler from version 1.3.0 when using version 1.5.1. This might lead to breaking code or invalid results. Use at your own risk. For more info please refer to:
https://scikit-learn.org/stable/model_persistence.html#security-maintainability-limitations
  warnings.warn(
Traceback (most recent call last):
  File "/Users/kyeong6/Desktop/github_submit/WVR/LSTM_pipeline/3_Prediction.py", line 101, in <module>
    main()
  File "/Users/kyeong6/Desktop/github_submit/WVR/LSTM_pipeline/3_Prediction.py", line 44, in main
    abnormal_detection.abnormal_detection(args.filename, args.criteria) # 이상탐지
  File "/Users/kyeong6/Desktop/github_submit/WVR/LSTM_pipeline/Abnormal_detection.py", line 158, in abnormal_detection
    x_data = create_x_new_data(df, window_size, sc)
  File "/Users/kyeong6/Desktop/github_submit/WVR/LSTM_pipeline/Abnormal_detection.py", line 81, in create_x_new_data
    x_data = np.reshape(x_data, (x_data.shape[0], x_data.shape[1], 1))
IndexError: tuple index out of range
```

해당 오류는 간단한게 표현하자면 데이터 길이(pipeline_sample.csv의 행의 개수)가 LSTM 모델에 필요한 window_size보다 작다는 의미이다. 

**디버깅 추가**

```bash
python 3_Prediction.py -f ./Input/pipeline_sample.csv -a                         
/Users/kyeong6/anaconda3/envs/lstm_pipeline/lib/python3.9/site-packages/sklearn/base.py:376: InconsistentVersionWarning: Trying to unpickle estimator MinMaxScaler from version 1.3.0 when using version 1.5.1. This might lead to breaking code or invalid results. Use at your own risk. For more info please refer to:
https://scikit-learn.org/stable/model_persistence.html#security-maintainability-limitations
  warnings.warn(
Data length: 60, Window size: 168
Traceback (most recent call last):
  File "/Users/kyeong6/Desktop/github_submit/WVR/LSTM_pipeline/3_Prediction.py", line 101, in <module>
    main()
  File "/Users/kyeong6/Desktop/github_submit/WVR/LSTM_pipeline/3_Prediction.py", line 44, in main
    abnormal_detection.abnormal_detection(args.filename, args.criteria) # 이상탐지
  File "/Users/kyeong6/Desktop/github_submit/WVR/LSTM_pipeline/Abnormal_detection.py", line 166, in abnormal_detection
    x_data = create_x_new_data(df, window_size, sc)
  File "/Users/kyeong6/Desktop/github_submit/WVR/LSTM_pipeline/Abnormal_detection.py", line 68, in create_x_new_data
    raise ValueError(f"Not enough data to create sequences. Data length: {data_len}, window size: {window_size}")
ValueError: Not enough data to create sequences. Data length: 60, window size: 168
```

디버깅 코드를 추가하여 확인해보면 2_Learning_LSTM.py 스크립트를 통해 모델을 학습할 때 window_size를 168으로 설정한 후 학습하여 예측하고자하는 데이터셋의 길이인 60으로는 예측을 진행할 수 없다는 것이다. 

프로젝트 취지에 맞게 60개의 행을 통해 예측을 하고자한다면 LSTM 모델을 학습시킬 때 window_size를 수정해줘야한다. 

**학습 코드 수정**

1. Training.py, Abnormal_detection.py에서 window_size 변수의 값 59로 설정하여 학습을 진행한다.
2. 2_Learning_LSTM.py에서 window_size, periods default 값을 59, 1로 각각 변경한다.

**학습 진행 후 에러 발생**

```bash
python 3_Prediction.py -f ./Input/pipeline_sample.csv -a
Data length: 60, Window size: 59
2024-07-22 15:05:47.412537: W tensorflow/core/platform/profile_utils/cpu_utils.cc:128] Failed to get CPU frequency: 0 Hz
1/1 [==============================] - 0s 246ms/step
이상치가 없습니다.
/Users/kyeong6/Desktop/github_submit/WVR/LSTM_pipeline/Data_preprocessing.py:82: FutureWarning: 'H' is deprecated and will be removed in a future version, please use 'h' instead.
  time_df = time_df.resample(time_interval).mean() # 평균값으로 병합
Traceback (most recent call last):
  File "/Users/kyeong6/Desktop/github_submit/WVR/LSTM_pipeline/3_Prediction.py", line 101, in <module>
    main()
  File "/Users/kyeong6/Desktop/github_submit/WVR/LSTM_pipeline/3_Prediction.py", line 45, in main
    predict.prediction(args.filename, args.criteria) # 예측 
  File "/Users/kyeong6/Desktop/github_submit/WVR/LSTM_pipeline/Prediction.py", line 112, in prediction
    x_data = abnormal_detection.create_x_new_data(df, window_size, sc)
  File "/Users/kyeong6/Desktop/github_submit/WVR/LSTM_pipeline/Abnormal_detection.py", line 68, in create_x_new_data
    raise ValueError(f"Not enough data to create sequences. Data length: {data_len}, window size: {window_size}")
ValueError: Not enough data to create sequences. Data length: 1, window size: 59
```

마지막 ValueError를 통해 동일한 문제가 있음을 알 수 있다. 

전처리 단계(Data_Preprocessing.py)에서 리샘플링하는 과정에서 데이터 길이가 줄어들어 발생한 문제라고 판단했다. 추가적으로 Data_Preprocessing.py를 수정해야한다.

**최종 결과**

iD+1h 개념을 도입하기 위해 많은 과정이 필요했는데 수정한 파일은 다음과 같다.

1. Data_preprocessing.py
2. 2_Learning_LSTM.py
3. 3_Prediction.py
4. Abnormal_detection.py
5. Prediction.py
6. Training.py

거의 모든 파일을 수정했으며 다음과 같은 예측값을 얻을 수 있다.

- pipeline_sample.csv(Input)

![스크린샷 2024-07-22 오후 4 49 13](https://github.com/user-attachments/assets/948fcddb-6413-4475-b7f1-1105ba11fe2c)


테스트 데이터는 2020-04-16 4:00 ~ 4:59 데이터를 사용했다.

- prediction.csv(Output)

![스크린샷 2024-07-22 오후 4 50 05](https://github.com/user-attachments/assets/55e1d2dd-f22f-4077-9f78-0496d3e2d41d)


iD+1H 형식으로 예측 결과값이 잘 나왔음을 알 수 있다.

### 3. 파이프라인 디렉토리 구조

**디렉토리 구조** 

```bash
project_root/
├── core/
│   ├── config.py                  # 경로, 환경변수 등 구성 파일
├── data/
│   ├── input/                     # lstm 예측을 위한 파일 
│   │   ├── sample.csv
│   ├── output/                    # Input에 기반하여 얻은 lstm 예측 사용 및 결과 파일
│   │   ├── Data_preprocessing/
│   │   │   ├── criteria.csv
│   │   │   └── preprocessed.csv
│   │   ├── Learning_lstm/
│   │   │   ├── lstm_model.h5
│   │   │   ├── lstm_performance_graph.tiff
│   │   │   └── scaler.pkl
│   │   └── Prediction/
│   │       └── prediction.csv
│   ├── raw/                       # 센서 관련 데이터
│   │   ├── from_sensor_data.txt   # 센서로부터 받은 데이터
│   │   ├── to_sensor_data.txt     # 센서로 보내야하는 데이터
├── db/
│   ├── crud.py                    # 데이터베이스 CRUD 작업 코드
│   ├── database.py                # 데이터베이스 연결
│   ├── models.py                  # 데이터베이스 테이블 설정
│   ├── schema.py                  # 데이터베이스 테이블 속성 정의 
├── src/                           # 소스 코드 디렉토리
│   ├── txt_transform.py           # txt 파일 추출 및 구성 파일
│   ├── database_utils.py          # 데이터베이스 적재 및 조회 수행
│   ├── outlier_detection.py       # 이상치 검출 파일
│   ├── csv_transform.py           # csv 파일 구성(input)
│   ├── lstm/                      # LSTM 예측 코드 
│   │   ├── 1_Preprocessing_tool.py
│   │   ├── 2_Learning_LSTM.py
│   │   ├── 3_Prediction.py
│   │   ├── abnormal_detection.py
│   │   ├── data_preprocessing.py
│   │   ├── prediction.py
│   │   └── training.py
│   ├── scheduling.py              # 스케줄링 적용 코드
├── logs/                          # 로그 파일 설정
│   ├── etl.log
│   ├── lstm.log
│   ├── outlier.log
│   └── errors.log
├── docs/                          
│   ├── architecture.md            # 데이터 파이프라인 구조 설명
│   ├── data_format.md             # 프로젝트에 사용되는 데이터 구조 설명
│   └── usage.md                   # 데이터 파이프라인 실행 방법 설명
├── errors/
│   ├── custom_exceptions.py       # 커스텀 예외처리 설정
│   ├── error_handler.py           # 예외처리 응답 
├── tests/                         # 기능 테스트(추후 업데이트) 
├── main.py                        # 실행 파일
```

모듈화에 초점을 맞춰 위와 같은 디렉토리 구조를 구상했다.

기능 실행에 관해서 간단하게 설명하면 다음과 같다.

CRUD(crud.py) $\subset$ API(src) $\subset$ 스케줄링(scheduling.py) $\subset$ main.py

또한, 디렉토리 구조를 구상해나가면서 기존에는 txt 파일의 데이터를 추출한 후 DB에 적재하고 이를 통해서 이상치 판단 & LSTM 예측 수행을 하려했으나 굳이 이럴 필요 없이 txt_transform.py에 존재하는 txt 데이터 추출 함수의 반환값을 통해 DB 적재 및 이상치 판단 혹은 LSTM 예측을 동시에 진행하는, 즉 2개의 프로세스로 구분하기로 결정했다. 

위 방식을 택하면 DB에 접근하는 횟수가 적어 시간적 비용을 아낄 수 있을거라 판단된다. 

**수정한 아키텍처**

![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/0c79766f-e6e5-47fb-bb1f-6711656123dd/97bd34c1-88d0-4970-8f9f-62a90e70901b/Untitled.png)