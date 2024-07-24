# 업무내용

- 파이프라인 세부사항 개발 시작

## 7/22 ~ 23

### 수행할 업무
1. 코드 작성 원칙
2. LSTM 모델 예측 iD+1h 개념 도입
3. 파이프라인 디렉토리 구조 구상
4. 파이프라인 구축 진행
5. LSTM 모델 1년에 한 번씩 Train 과정 수행

### 1. 코드 작성 원칙

해당 프로젝트는 데이터 파이프라인을 구축을 해야한다. 이에 따른 코드 작성 원칙을 세워보고자 한다. 

1. 함수화, 모듈화 및 클래스를 사용하자
2. 추후 변경에 용이하게 주석 처리를 잘 하자
3. 변수명과 디렉토리명을 명확하게 작성하자

### 2. LSTM 모델 예측 iD+1h 개념 도입

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

모듈화에 초점을 맞춰 디렉토리 구조를 구상했다. (상세한 디렉토리 구조는 생략)

기능 실행에 관해서 간단하게 설명하면 다음과 같다.

CRUD(crud.py) $\subset$ API(src) $\subset$ 스케줄링(scheduling.py) $\subset$ main.py

또한, 디렉토리 구조를 구상해나가면서 기존에는 txt 파일의 데이터를 추출한 후 DB에 적재하고 이를 통해서 이상치 판단 & LSTM 예측 수행을 하려했으나 굳이 이럴 필요 없이 txt_transform.py에 존재하는 txt 데이터 추출 함수의 반환값을 통해 DB 적재 및 이상치 판단 혹은 LSTM 예측을 동시에 진행하는, 즉 2개의 프로세스로 구분하기로 결정했다. 

위 방식을 택하면 DB에 접근하는 횟수가 적어 시간적 비용을 아낄 수 있을거라 판단된다. 

**수정한 아키텍처**

<img width="1920" alt="LSTM-pipeline" src="https://github.com/user-attachments/assets/6818bd91-2ffb-4dfc-af0f-bbc293c02b95">


### 4. 파이프라인 구축 진행

**1-1. 기존 LSTM 경로 수정**

현재 예측값 도출 구조는 LSTM_pipeline으로 설정되어있어 프로젝트를 확장하면 이에 따라 경로 수정이 필요하다. 

즉, src/lstm에 위치한 스크립트에서 사용하는 criteria.csv, preprocessed.csv, prediction.csv 등의 저장 경로를 data/output으로 변경이 필요하다.

**1-2. Root 디렉토리를 Project root로 설정**

환경변수를 사용하여 경로를 설정했다. 환경변수는 core/config.py에 존재하여 src/lstm/{file} 해당 파일 스크립트에 `from core.config import settings` 를 작성하면 `ModuleNotFoundError`가 발생한다. 

이를 해결하기 위해서 다음과 같은 코드를 작성하여 해결했다.

```python
import sys
import os 

# Root directory를 Project Root로 설정
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.append(project_root)
os.chdir(project_root)
```

- project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
    - core 디렉토리에 접근하기 위해 두 레벨 (’../../’) 위로 올라간 후 절대경로로 변경
- sys.path.append(project_root)
    - sys.path에 project_root를 추가하여 core.config 가져오기 올바르게 작동
- os.chdir(project_root)
    - 작업 디렉토리를 project_root로 변경하여 수행하는 스크립트의 작업이 프로젝트 루트(not project_root)와 관련된 파일 탐색(data/ …)

**1-3.명령어 예시**

명령어 프로젝트 루트인 WVR 디렉토리에서 실행한다.

- 1_Preprocessing_tool.py

```bash
python src/lstm/1_Preprocessing_tool.py -f data/input/sample.csv -p
```

- 2_Learning_LSTM.py

```bash
python src/lstm/2_Learning_LSTM.py -l
```

- 3_Prediction.py

```bash
python src/lstm/3_Prediction.py -f data/input/pipeline_sample.csv -a
```

**2-1. CRUD 작업 스크립트 : crud.py** 

프로젝트에서 다수의 CRUD 작업이 존재한다. 사용되는 CRUD 작업을 함수화하여 src에 존재하는 기능 스크립트들이 함수(기능)를 호출하여 진행하고자 한다.(모듈화)

- 테이블 생성(Create)
- LSTM 예측 진행을 위한 조회(Read)
- 실제값 적재(Load)
- 이상치, 예측값 적재(Load)

**2-2. txt 변환 스크립트 : transform.py**

첫 번째와 마지막 단계인 txt 변환 작업을 수행하는 transform.py의 필요한 요소는 다음과 같다.

- Database
    - txt 파일을 읽어 데이터베이스에 적재하는 함수
- 이상치
    - txt 파일을 읽어 이상치 판단에 사용할 수 있게 반환값 설정하는 함수
    - 이상치 판단 스크립트의 반환값을 txt로 변환한 후 sensor/to_sensor_outlier_data.txt 위치시키는 
    함수
- 예측
    - txt 파일을 읽어 csv 형식으로 변환하여 input 디렉토리에 위치시키는 함수
    - prediction.csv을 txt로 변환한 후 sensor/to_sensor_pred_data.txt 위치시키는 함수

transform.py에는 3개의 객체(Class)로 나눌 수 있어 3개의 클래스 내부에 기능(함수)를 넣을 예정이다.

**2-3. LSTM 예측 스크립트**

src/lstm 디렉토리의 파일들은 앞선 업무 일지에서 정리했기 때문에 생략한다.

**2-4. 이상치 검출 스크립트 : outlier_detection.py**

이상치 검출은 4가지 단계가 존재한다. 

- System abnormal
- Real value abnormal
- Prediction value abnormal
- Night flow abnormal

4가지 검출 방법에서 유량은 4개 모두, 수압력은 Night flow abnormal을 제외한 3가지를 적용한다. 

유량, 수압력 2개의 객체(Class)로 나누어 검출 방법을 함수화하여 클래스 내부에 넣을 예정이다. 

**2-5. 스케줄링 스크립트 : scheduling.py**

2-1 ~ 2-4 스크립트에 작성한 기능을 호출해서 특정 시간에 수행할 수 있게 스케줄링을 적용한다. 

최종적으로 scheduling.py에 존재하는 함수(or Class)를 루트 디렉토리에 존재하는 main.py에서 호출하여 실행하는 구조이다. 

**2-6. 기능 수행 결론**

CRUD(crud.py) $\subset$ API(src) $\subset$ 스케줄링(scheduling.py) $\subset$ main.py