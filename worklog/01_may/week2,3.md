## Setting

### 순서

1. conda 설치(python 가상환경 제공)
2. LSTM_pipline 디렉토리 이동

```bash
# 이동
cd /{user_path}/LSTM_pipeline
```

1. LSTM_pipeline 가상환경 설치

```bash
conda env create -f lstm_env.yaml
```

MAC OS에서는 `PackagesNotFoundError: The following packages are not available from current channels:` 발생

해당 오류는 Guideline에서 설명하는 OS는 Window이기 때문에 MAC OS에 호환되게 yaml 파일 수정이 필요하다. 

**MAC OS에 호환되는 lstm_env.yaml 수정본**

```yaml
name: lstm_env
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.9
  - ipykernel
  - ipython
  - ipywidgets
  - jupyter
  - jupyter_client
  - jupyter_console
  - jupyter_core
  - jupyterlab
  - matplotlib
  - numpy
  - pandas
  - scipy
  - tensorflow=2.10.0
  - h5py
  - keras=2.10.0
  - scikit-learn
  - seaborn
  - pillow
  - requests
  - pyyaml
  - protobuf
  - libclang
  - aiohttp
  - async-timeout
  - attrs
  - bcrypt
  - beautifulsoup4
  - bleach
  - cffi
  - charset-normalizer
  - cryptography
  - decorator
  - defusedxml
  - gast
  - grpcio
  - idna
  - importlib-metadata
  - markdown
  - oauthlib
  - openssl
  - pandas
  - parso
  - pickleshare
  - prompt-toolkit
  - pygments
  - pyjwt
  - pyparsing
  - pyrsistent
  - python-dateutil
  - pytz
  - requests
  - rsa
  - setuptools
  - six
  - sqlite
  - tensorboard
  - termcolor
  - tornado
  - typing_extensions
  - urllib3
  - wheel
  - widgetsnbextension
  - zipp

prefix: /Users/{username}/anaconda3/envs/lstm_env
```

prefix는 conda설치 경로를 작성하면 된다.

1. lstm_env 활성화

```bash
conda activate lstm_env
```

---

## 1_Preprocessing_tool.py

### 실행 명령어

```bash
python 1_Preprocessing_tool.py -f /Users/kyeong6/Desktop/github_submit/WVR/LSTM_pipeline/Input/sample.csv -p
```

### **arguments**

- -h : parse_arguments()의 인자들에 대한 설명 출력(help 기능)
- -f : filename을 입력, 즉 Input 디렉토리에 위치한 시계열 데이터(time, value로 구성)를 입력 파일로 설정
- -n : normal_range의 의미로 정상범위를 정함(기본값 존재)
- -m1 : min을 의미하며, 정상 범위의 최솟값을 지정한다.
- -m2 : max를 의미하며, 정상 범위의 최댓값을 지정한다.
- -l : level의 의미로 이상치 보정시, 정상범위에서의 이상치 허용 기준(기본값 10% 존재)
- -w : week의 의미로 주말 혹은 평일 데이터 저장(기본값 all)
- -t : time의 의미로 시간 간격을 조정
    - hourly : 시간당
    - daily : 일당
- -p : preprocess의 의미로 특정한 인자의 값으로 데이터 전처리 진행(-f 입력 필요)
    - -f를 입력하면 다른 인자들은 기본값으로 실행

해당 파일은 데이터셋 전처리를 위한 CLI 도구 역할을 한다. argparse 라이브러리를 통해 명령줄 옵션 정의 및 parsing하며, Data_preprocessing 모듈 함수 사용하여 실제 데이터 작업 수행

### main() 함수

- `preprocessing = importlib.import_module('Data_preprocessing')` 작성한 이유
    - `Data_preprocessing.py`를 참조하여 main()가 실행

- main()

```python
def main():
    args = parse_arguments()

    if not args.preprocess: 
        # 데이터 읽어오기
        df = preprocessing.read_data(args.filename) 
        # # 결측치 보정
        df = preprocessing.Missing(df) 

        if args.time is not None: 
            # 시간 간격 병합
            time_interval = {'hourly': '1H', 'daily': '1D'}.get(args.time)
            df = preprocessing.TimeIntervalData(df,time_interval)

        if args.normal_range:
            # 이상치 보정
            df, table = preprocessing.Anomalous(df, args.level, args.max, args.min)

        # 평일 / 주말 데이터 구하기    
        if args.week in ['weekday', 'weekend']:
            df = preprocessing.week(df,args.week)

        # 전처리한 데이터 저장
        preprocessing.save_data(df, table)
    else:
        # 데이터 전처리 : 시간 병합(daily), 이상치 보정(level: 10%, 정상범위: UIF or LIF), 전체 데이터(week: all)
        preprocessing.Data_preprocessing(args.filename, args.level)
```

- `if not args.preprocess` 조건문
    - 위 parser.add_argument의 -p 옵션에 해당하는 --preprocess가 설정되지 않았을 때 실행함을 의미한다. 즉, 사용자가 input data의 전처리를 세부적으로 제어하고자 할 때 조건문 블록 내의 코드가 실행
- `else`
    - --preprocess가 설정된 경우, 기본값으로 설정된 인자들로 데이터 전처리 수행

---

## Data_preprocessing.py

<aside>
💡 1_Preprocessing_tool.py은 Data_preprocessing.py를 import하여 CLI를 진행한다. 
따라서 Data_preprocessing.py의 main()의 흐름에 맞게 정리가 필요하다.

</aside>

### 순서

1. 데이터 읽어오기(Input의 time/values)
2. 결측치 처리
3. 시간 간격으로 병합(hourly, daily)
4. 이상치 보정
5. 평일과 주말 데이터 추출(선택)
6. 전처리한 데이터, 원본 데이터의 통계 테이블 저장
    1. 경로 : ./Output/Data_preprocessing

### 환경 설정

```python
import os
import pandas as pd
import sys

os.chdir(os.path.dirname(__file__))
```

- 필요한 라이브러리 설치
- `os.chdir(os.path.dirname(__file__))`
    - __file__ : 현재 파일 path를 반환
    - os.path.dirname(__file__) : 현재 파일 path의 디렉토리명 반환
    - os.chdir(os.path.dirname(__file__))
        - script가 실행되는 디렉토리를 script file이 위치한 디렉토리로 변경
        
        → 상대 경로를 사용할 때 문제가 없도록 해줌(협업시 문제 x)
        

### 데이터 읽기(read_data)

```python
def read_data(file_name):
    df = pd.read_csv(file_name,index_col = 0) 

    # 데이터프레임 인덱스를 데이트타임인덱스로 변환
    df.index = pd.to_datetime(df.index)
    df.index.name = 'time'

    # values 이름 추출
    col = df.columns[0]

    # float 변환
    df[col] = pd.to_numeric(df[col], errors='coerce') 
    df[col] = df[col].astype(float)
    
    # 인덱스 정렬
    df = df.sort_index(ascending=True) 
    return df

```

- df 설정 → 1_Preprocessing_tool.py에서 -f 인자를 이용하여 입력한 파일명
- 파일에 존재하는 값들 각각 `datetime`, `float` 으로 타입 변환 진행 후 인덱스 오름차순 정렬
- df 반환

**1_Preprocessing_tool.py**

```python
def main():
    args = parse_arguments()

    if not args.preprocess: 
        # 데이터 읽어오기
        df = preprocessing.read_data(args.filename)
```

해당 부분까지 진행

### 결측치 보정(Missing)

- 연속적인 결측치 3개 이하이면 이전의 값 대체, 초과이면 선형 보간을 사용하여 결측치를 채움

```python
def Missing(df):
    n = 0
    first_column = df.iloc[:, n]

    # in case first line is null
    if first_column.isnull().iloc[0]:
        first_non_nan_index = first_column.first_valid_index()
        df = df.loc[first_non_nan_index:]

    # in case last lines are missing
    nan_list = list(first_column.isnull())
    if nan_list[-1]:
        last_non_nan_idx = first_column.last_valid_index()
        df = df.loc[:last_non_nan_idx]

    # in case greater than 3
    method_fill = 'ffill'  # replace previous values
    count = 0
    for i, v in enumerate(first_column.isnull()) : 
        if v:
            count += 1
        else:
            if count > 3:
                df.iloc[i - count-1:i+1, n] = df.iloc[i - count-1:i+1, n].interpolate()  # replace with interpolation
            else: # in case missing values are less than equal to 3
                df.iloc[i - count-1:i, n].fillna(method=method_fill, inplace=True)
            count = 0
   
    return df
```

- 첫 번째 조건문(if first_column.isnull().iloc[0]) : 첫 행 결측치 처리
    - 첫 행이 만약 결측치라면 결측치가 아닌 첫 행을 찾아서 그 행 이후 데이터만 유지
    - **선형보간법에서 첫번째 점에 해당**
- 두 번째 조건문(if nan_list[-1]) : 마지막 행 결측치 처리
    - 마지막 행이 만약 결측치라면 결측치가 아닌 유효한 마지막 인덱스를 찾아 해당 행까지 데이터만 유지
    - **선형보간법에서 마지막 점에 해당**
- enumerate를 이용해 null 값 count 진행(결측치 값 카운트)
- 연속된 결측치 3개 초과(if count > 3)
    - 해당 범위에 대해 선형 보간(interpolate) 진행하여 결측치 채움
- 연속된 결측치 3개 이하(else)
    - method_fill의 값인 ffill, 즉 결측치를 이전 값을 사용해 채움

### 시간 간격으로 병합

```python
def TimeIntervalData(df,time_interval): 

    time_df = df.sort_index(ascending=True)
    time_df = time_df.resample(time_interval).mean() # 평균값으로 병합

    # time의 결측치 확인
    if time_df.isnull().any().any():
        time_df = Missing(time_df) 

    return time_df
```

- 데이터를 지정된 시간 간격(time_interval)으로 재표본화하고 각 간격의 평균값 계산
    - 시간 간격 일관되게하여 분석, 모델링에 적합
- 1_Preprocessing_tool.py

```python
if args.time is not None: 
            # 시간 간격 병합
            time_interval = {'hourly': '1H', 'daily': '1D'}.get(args.time)
            df = preprocessing.TimeIntervalData(df,time_interval)
```

TimeIntervalData의 매개변수인 time_interval을 1_Preprocessing_tool.py에서 지정이 가능하다. 

- 기준
    - hourly : 1H
    - daily : 1D

-t 인자를 terminal에 작성할 때 hourly 혹은 daily를 함께 작성해줘야 하는 이유이다.

```python
# 예시
python 1_Preprocessing_tool.py -t hourly
```

**재표본화 예시**

- 기존 값

```python
                     Value
2024-01-01 00:00:00     44
2024-01-01 00:01:00     47
2024-01-01 00:02:00     64
2024-01-01 00:03:00     67
2024-01-01 00:04:00     67
2024-01-01 00:05:00     9
2024-01-01 00:06:00     83
2024-01-01 00:07:00     21
2024-01-01 00:08:00     36
2024-01-01 00:09:00     87
```

- 재표본화(각 간격의 평균값 계산)

```python
# 5분 간격으로 데이터 재표본화 후 평균값 계산
resampled_df = df.resample('5T').mean()
print(resampled_df)
```

- 변형값

```python
                     Value
2024-01-01 00:00:00   57.8
2024-01-01 00:05:00   47.2
```

첫 번째 행은 00:00:00 ~ 00:04:00의 값의 평균

두 번째 행은 00:05:00 ~ 00:09:00의 값의 평균

### 이상치 보정

- 입력받은 퍼센트 값에서 벗어나는 값 정상범위로 보정

```python
def Anomalous(df, percent, normal_max=None, normal_min=None): 
    col = df.columns[0]
    
    # 원본 데이터의 최댓값, 최솟값 계산
    MAX = df[col].max()        
    MIN = df[col].min()
    
    # 정상범위가 없는 경우 : UIF, LIF 
    if normal_max is None and normal_min is None: 
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        IQR = q3 - q1
        UIF = q3 + (IQR * 1.5)
        LIF = q1 - (IQR * 1.5)
        normal_max = UIF 
        normal_min = LIF
    
    # criteria.csv 생성
    table = pd.DataFrame({'Values': [ MIN, MAX, normal_min, normal_max] },
                index=['raw_min', 'raw_max', 'normal_min', 'normal_max'])

    # 이상치 보정
    if normal_max is not None: # 정상범위의 최댓값이 있는 경우
        # U_level 계산
        U_level =  (abs(MAX - normal_max) * (percent * 0.01)) +  normal_max
        table.loc['U_level'] = U_level # table에서 U_level를 추가
        
        # 데이터의 최댓값이 정상범위의 최댓값보다 크면 정상범위의 최댓값으로 대체 
        if MAX > normal_max:
            df.loc[df[col] > U_level] = normal_max

    if normal_min is not None: # 정상범위의 최솟값이 있는 경우
        # L_level 계산
        L_level = normal_min - (abs(normal_min - MIN) * (percent * 0.01))   
        table.loc['L_level'] = L_level # table에서 L_level 추가

        # 데이터의 최솟값이 정상범위의 최솟값보다 크면 정상범위의 최솟값으로 대체 
        if MIN < normal_min:
            df.loc[df[col] < L_level] = normal_min
           
    return df, table
```

- col = df.columns[0] : value값 존재
- MIN, MAX : criteria.csv에 넣을 값
- UIF, LIF : normal_max, normal_min이 지정되지 않았을 경우 데이터의 1사분위, 3사분위(q1, q3)을 기반으로 내부 울타리 계산(데이터의 정상성)
- 1_Preprocessing_tool.py

```python
python 1_Preprocessing_tool.py -n -m1 -m2
```

-n을 통해 정상범위(default)로 정할 수 있고, -m1, -m2를 통해서 정상범위 지정 가능

**Anomalous 함수는 normal_max, normal_min이 `None` 으로 설정되어있기 때문에 지정 필요**

- 위 과정을 진행한 후 table 생성
    - table은 ./Output/Data_preprocessing/creteria.csv에 저장
    - index : raw_min, raw_max, normal_min, normal_max
    - 위 인덱스에 각각 위 과정을 통해 얻은 MIN, MAX, normal_min, normal_max 값 넣음

- 이상치 보정 진행
    - 정상범위의 최댓값이 있는 경우(if normal_max is not None)
        - 이상치 보정 수준(U_level)을 계산
        - 실제 최댓값(MAX)이 정상범위의 최댓값보다 크면 정상범위의 최댓값으로 대체
    - 정상범위의 최솟값이 있는 경우(if normal_min is not None)
        - 이상치 보정 수준(L_level)을 계산
        - 실제 최솟값(MIN)이 정상범위의 최솟값보다 크면 정상범위의 최솟값으로 대체

- 이후 df 및 table 반환

**위 과정을 통해 최댓값 혹은 최솟값의 값들이 너무 높거나 낮을 경우 조정하여 이상치를 줄일 수 있음**

### 평일과 주말 데이터 추출

```python
def week(df,day_of_week):
        if day_of_week == 'weekend':
            return df[df.index.dayofweek.isin([5, 6])]  # 5: 토요일, 6: 일요일
        
        if day_of_week == 'weekday':
            return df[df.index.dayofweek.isin([0, 1, 2, 3, 4])]  # 0~4: 월요일부터 금요일까지
```

df.index.dayofweek는 pandas 라이브러리에서 datetime 데이터 타입의 값의 요일을 나타내는 정수를 반환

| 요일 | 정수 |
| --- | --- |
| 월요일 | 0 |
| 화요일 | 1 |
| 수요일 | 2 |
| 목요일 | 3 |
| 금요일 | 4 |
| 토요일 | 5 |
| 일요일 | 6 |
- 1_Preprocessing_tool.py

```python
python 1_Preprocessing_tool.py -w weekday
```

weekday : 평일

weekend : 주말

### 데이터 저장

```python
def save_data(df, table):

    # 폴더 생성
    output_path = './Output/Data_preprocessing'
    os.makedirs(output_path, exist_ok=True)

    # 전처리한 데이터, 원본 데이터의 criteria 저장
    df.to_csv(f'{output_path}/preprocessed.csv')  
    table.to_csv(f'{output_path}/criteria.csv')
```

위 과정들을 진행한 후의 결과물(output)을 저장

- df :  preprocessed.csv
- table : criteria.csv

### 기본값 실행

<aside>
💡 1_Preprocessing_tool.py에서 if not args.preprocess의 else 부분 실행시킬 때 사용하는 기능
 -p 인자를 사용하며 기본값을 이용해서 데이터 전처리 실행

</aside>

```python
def Data_preprocessing(file_name, percent):
    
    # 데이터 읽어오기
    df = read_data(file_name)

    # 결측치 보정
    df = Missing(df)

    # 데이터 병합 (1D)
    time_interval = '1D'
    df = TimeIntervalData(df,time_interval)
    
    # 이상치 보정
    df, table = Anomalous(df, percent, normal_max=None, normal_min=None)

    # 평일 / 주말 데이터 구하기
    day_of_week = 'all'
    if day_of_week != 'all':
        df = week(df,day_of_week)

    # 전처리한 데이터, 원본 데이터의 criteria 저장
    save_data(df, table)
```

-p 인자로 실행할 때 -f를 입력해야 하는 이유 : Data_preprocessing의 매개변수로 file_name 존재

```python
if __name__ == "__main__":
    file_name = sys.argv[1]
    percent = sys.argv[2]

    Data_preprocessing(file_name, percent)
```

sys.argv를 통해 해당 terminal의 값이 각각 file_name, percent 변수에 담기고 Data_preprocessing(기본값 실행)의 매개변수 값으로 사용

**참고**

sys.argv[0] : 파일명

sys.argv 순서가 존재하므로 -f 인자를 먼저 작성한 후 -l 인자 작성

---

## 2_Learning_LSTM.py

Data_preprocessing을 통해 얻은 `criteria.csv`, `peprocessed.csv` 을 이용하여 시계열 분석 모델인 `LSTM` 을 실행한다.

### **arguments**

- -h : parse_arguments()의 인자들에 대한 설명 출력(help 기능)
- -f : 전처리한 파일 이름을 입력(preprocessed.csv)
- -c : 원본 데이터의 통계 파일 이름 입력(criteria.csv)
- -w : 윈도우 사이즈 설정
- -p : 예측 윈도우 사이즈 설정
- -hp : hyper parameter 설정(-e, -b 같이 사용)
    - -e : epoch 설정
    - -b : batch size 설정hourly : 시간당
- -l : learning의 의미로 특정한 인자의 값(default)으로 데이터 전처리 진행
    - -f, -c 입력 필요(default로 실행)

`-l` 옵션은 1_Preprocessing_tool.py의 `-p` 와 동일

### main()

```python
import importlib
import argparse

preprocessing = importlib.import_module('Data_preprocessing')
training = importlib.import_module('Training')

def main():
    args = parse_arguments()

    if args.learning: 
        training.training(7, 1)

    else:
        # 데이터 읽어오기
        df = training.read_data(args.filename)
    
        # 학습 데이터 / 테스트 데이터 분할
        train, test = training.train_test_split(df)

        # 데이터 스케일링
        sc = training.data_scaling(train)

        # x_train, y_train, x_test 생성
        x_train, y_train = training.create_train(train, args.window_size, args.periods, sc)
        x_test = training.create_x_test(test, args.window_size, sc)

        # 모델 생성
        lstm_model = training.lstm_arch(x_train, y_train, args.periods, args.epochs, args.batch_size)

        # 모델 성능 평가 
        plot = training.lstm_performance(lstm_model, sc, x_test, test, args.epochs, args.batch_size)

        # 스케일러, 모델, 그래프 저장
        training.save_output(sc, lstm_model, plot)

```

- `if args.learning` 은 -l 옵션(default 값)을 사용했을 경우 실행
- `training.training(7,1)`은 Training.py에 존재하는 training(window_size, periods)를 실행
    - `Training.py` 은 main()에 정의되어 있는 함수들의 내용들이 존재하는 파일
- else 부분은 Training.py를 이용하여 설명

---

## Training.py

`Training.py` 은 2_Learning_LSTM.py를 실행하기 위한 함수들 정의된 파일이다.

### 순서

1. 데이터 읽어오기
    1. preprocessed.csv
2. train / test split (7:3)
3. Scaling
4. x_train, y_train, x_test 생성
5. 모델 성능 평가
6. Learning_lstm directory에 결과값 저장
    1. 스케일러 : scaler.pkl
    2. LSTM 모델 : lstm_model.pkl
    3. LSTM 성능 평가 그래프 : lstm_performance_graph.tiff

### Import

```python
from keras.models import Sequential
from keras.layers import Dense, LSTM
from tensorflow.keras.optimizers import SGD
from sklearn.preprocessing import MinMaxScaler
from keras.metrics import MeanSquaredError
import matplotlib.pyplot as plt
from joblib import dump
import pandas as pd
import numpy as np
import sys
import os
```

- `from keras.models import Sequential`
    - Keras에서 모델을 층(layer)별로 만드는 방법 제공, 선형적으로 층을 쌓을 수 있게 해줌
- `from keras.layers import Dense, LSTM`
    - Keras에서 제공하는 층(layer) 중 하나인 완전 연결 층으로, 해당 층의 각 뉴런이 이전 층의 모든 뉴런과 연결
    - 시계열 분석 모델 제공
- `from tensorflow.keras.optimizers import SGD`
    - SGD(확률적 경사 하강법) 최적화 알고리즘 제공
- `from sklearn.preprocessing import MinMaxScaler`
    - 특정 범위 스케일링 방식인 MinMaxScaler 제공
- `from keras.metrics import MeanSquaredError`
    - 회귀 모델 성능 평가하는 MSE(평균 제곱 오차) 제공
- `from joblib import dump`
    - Python 객체를 디스크로 저장하고 불러오는데 사용, scikit-learn 모델을 효율적으로 저장하고 로드할 때 사용

### 환경변수 설정

```python
os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"]="0"
```

CUDA를 사용하는 GPU 디바이스 설정 코드

1. **`os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"`**
    1. CUDA 디바이스의 순서를 PCI 버스 ID 순서로 설정 즉, CUDA가 디바이스를 인식하고 사용하는 순서를 PCI 버스 ID의 순서로 진행
    2. 해당 코드를 작성하면 여러 개의 GPU가 있을 경우에도 각 GPU를 명확하게 식별이 가능
2. **`os.environ["CUDA_VISIBLE_DEVICES"]="0"`** 
    1. CUDA_VISIBLE_DEVICES 환경 변수를 설정, 이 변수는 CUDA가 사용할 수 있는 디바이스를 지정하는 데 사용된다. 
    2. "0"은 첫 번째 GPU를 의미 즉, CUDA는 이 코드 이후에 첫 번째 GPU만 사용하도록 설정.

위의 코드는 다중 GPU 시스템에서 특정 GPU를 선택하여 사용하고자 할 때 유용하다. 
    

### 데이터 읽어오기(read_data)

```python
def read_data(filename):
    df = pd.read_csv(filename, 
                    parse_dates=['time'], index_col=0)
    col = df.columns[0]
    df[col] = df[col].astype(float)

    return df
```

- read_data 함수의 인수는 전처리 된 파일인 `preprocessed.csv`
- csv 파일 형식

```
time,JM1_p
2020-01-01,4.145388888888888
2020-01-02,4.153791666666667
```

pd.read_csv의 인수인 `parse_dates` 는 `True` 로 설정할 경우 인덱스를 datetime 형식으로 변환

list 형식으로 넣을 경우(해당 코드 [’time’]) 리스트에 해당하는 컬럼을 datetime 형식으로 변환

`index_col` 은 인덱스에 넣어줄 컬럼을 지정

즉, df는 기존 preprocessed.csv에 time 컬럼에 존재하는 값을 datetime으로 변경한 후 Index로 사용한다. 그러므로 `df.columns[0]` 는 JM1_p가 된다. 이후 JM1_p의 데이터 타입은 float형으로 변환

- read_data 함수 실행 후 csv 파일 구조

```
                      JM1_p
time                       
2020-01-01  4.145388888888888
2020-01-02  4.153791666666667
```

| index | col[0] |
| --- | --- |
| time | JM1_p |

### 학습 데이터 / 테스트 데이터 분할 (7:3)

```python
def train_test_split(df):
    train_size = int(0.7 * len(df))
    train = df.iloc[:train_size]
    test = df.iloc[train_size:]

    return train, test
```

- read_data함수가 반환하는 df를 인수로 받아 모델 학습을 진행하기 위한 train / test 데이터 분할 진행
- 해당 함수에서는 분할 비율을 `train : test = 7 : 3` 로 설정
- 2_Learning_LSTM.py

```python
# 학습 데이터 / 테스트 데이터 분할
train, test = training.train_test_split(df)
```

각각 비율에 맞게 train, test 변수로 데이터가 들어감

### 데이터 스케일링

```python
def data_scaling(train):
    train_data = train.values
    sc = MinMaxScaler(feature_range=(0, 1)) # 정규화 
    sc = sc.fit(train_data) 

    return sc
```

`train_test_split` 를 통해 얻은 train 데이터를 data_scaling 인수로 하여 MinMaxScaler 정규화 진행

- **MinMaxScaler**
    
    ### 데이터 스케일링(Data Scaling)
    
    **서로 다른 변수의 값 범위를 일정한 수준으로 맞추는 작업 의미**
    
    값을 조정하는 과정이기 때문에 수치형 변수만 적용
    
    ### MinMaxScaler
    
    Scale을 조정하는 정규화 함수로, 모든 데이터가 0과 1 사이의 값을 갖도록 해주는 함수
    
    즉, 최댓값은 1, 최솟값은 0으로 데이터의 범위를 조정
    
    **알고리즘 성능 향상**
    
    ML 알고리즘은 입력 데이터의 스케일에 민감하기 때문에 데이터를 정규화하여 모델의 성능 향상
    
    **이상치 처리**
    
    이상치는 데이터의 일반적인 분포를 왜곡시킬 수 있으므로 스케일링을 통해 대다수의 데이터가 0~1 사이에 있으므로 이상치의 영향을 줄이는 데 도움
    
    ### 왜 훈련 데이터만 스케일링?
    
    모델을 학습할 때 사용되는 데이터셋(train 데이터셋)의 통계적 특성을 기준으로 스케일링을 수행하기 때문 
    
    이는 모델이 학습할 때 보지 못한 데이터(test 데이터셋 or 새로운 데이터)를 예측할 때 일관성 있게 스케일링을 적용
    
    해당 방식을 사용함으로써 모델이 test 데이터나 새로운 데이터에 대해서도 일관된 예측 수행이 가능
    

### x_train, y_train, x_test 생성

해당 부분은 시계열 데이터를 처리하여 LSTM 모델을 학습하기 위한 학습 데이터셋을 생성하는 코드이다.

```python
# x_train, y_train 생성
def create_train(train,window_size, periods, sc):
    
    train_data = train.values
    train_len = len(train_data)
    
    # 데이터 스케일링
    train_scaled = sc.transform(train_data)
    
    # x, y 학습데이터 생성
    x_train = []
    y_train = []
    for i in range(train_len - window_size - periods + 1):
        x_train_end = i+window_size
        x_train.append(train_scaled[i:x_train_end, 0]) 
        y_train.append(train_scaled[x_train_end:x_train_end+periods, 0])
    
    # 리스트를 넘파이 배열로 변환
    x_train, y_train = np.array(x_train), np.array(y_train)

    # x_train를 텐서로 변환
    x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))

    return x_train, y_train

```

- create_train(train, window_size, periods, sc) 인수 설명
    - train : train_test_split()에서 7대3 비율로 나눈 train data
    - window_size
        - 시계열 데이터를 분석 할 때 사용되는 개념, 시계열 데이터에서 각 데이터 포인트를 특정 기간의 데이터를 사용하여 예측하는데 사용
        - 즉, 모델이 과거 데이터를 살펴볼 시간 범위를 표현
        - 예를 들어 window_size의 값이 10이라면 10개의 이전 데이터 포인트를 사용하여 예측 수행
    - periods
        - 시계열 데이터에서 예측할 미래 시점의 기간 설정
        - 즉, periods는 모델이 예측할 시점으로부터 얼마나 떨어진 미래의 데이터를 예측할 것인지 결정
        - 예를 들어 periods의 값이 3이라면 모델은 다음 3개 시점에 대한 데이터 포인트를 예측
    - sc : 스케일링(MinMaxScaler)을 진행한 훈련 데이터

**순서**

- train 데이터의 값에 대한 데이터 스케일링 처리
    - data_scaling 함수에서 fit 과정을 하였지만 스케일링 과정을 완료하려면 transform도 수행

```python
# x, y 학습데이터 생성
    x_train = []
    y_train = []
    for i in range(train_len - window_size - periods + 1):
        x_train_end = i+window_size
        x_train.append(train_scaled[i:x_train_end, 0]) 
        y_train.append(train_scaled[x_train_end:x_train_end+periods, 0])
```

- x_train
    - 모델에 입력될 학습 데이터로 각각의 데이터 포인트는 이전의 데이터를 나타내는 시퀀스, 해당 시퀀스 길이는 `window_size` 에 의해 결정
- y_train
    - x_train 이후에 예측할 미래의 데이터를 표현, 미래 데이터의 기간은 `periods` 에 의해 결정
- 반복문에서의 i : 현재 시간 창의 시작 지점
- x_train_end :  현재 시간 창의 끝, 즉 i에 window_size를 더한 값
- train_scaled[i:x_train_end, 0] : 현재 시간 창에 해당하는 데이터를 x_train에 추가
- train_scaled[x_train_end:x_train_end + periods, 0] :  현재 시간 창 이후의 periods 크기만큼의 미래 데이터를 y_train에 추가

결론 : `x_train` 은 LSTM 모델에 입력되고, 해당 시간 창 이후의 `y_train` 은 모델의 실제 예측값과 비교하여 학습 이루어짐

- x, y 학습 데이터를 생성한 후 모델학습을 위해 numpy, tensor(x_train)로 변환 진행

```python
# x_test 생성
def create_x_test(test,window_size, sc):
    test_data = test.values
    test_len = len(test_data)    
    
    # 데이터 스케일링
    test_scaled = sc.transform(test_data)
    
    # x 테스트 데이터 생성
    x_test = []
    for i in range(test_len - window_size):
        x_test_end = i+window_size
        x_test.append(test_scaled[i:x_test_end, 0]) 
    
    # 리스트를 넘파이 배열로 변환
    x_test =  np.array(x_test)

    # x_test를 텐서로 변환
    x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))

    return x_test
```

- create_x_test(test, window_size, sc) 인수 설명
    - test : train_test_split 함수에 의해 반환된 test를 인수로 사용
    - window_size : create_train의 window_size와 동일
    - sc : 스케일링(MinMaxScaler)을 진행한 훈련 데이터
- 상세 코드는 create_train 함수와 동일

### 모델 생성

```python
def lstm_arch(x_train, y_train, periods, epochs, batch_size):
    # 모델 구성 (LSTM 레이어 2개, 활성화함수: 하이퍼볼릭탄젠트 사용)
    lstm_model = Sequential([
        LSTM(units=50, return_sequences=True, input_shape=(x_train.shape[1], 1), activation='tanh'),
        LSTM(units=50, activation='tanh'),
        Dense(units=periods) 
    ])
    
    # 모델 컴파일 (optimizer : SGD, 손실함수: MSE 사용)
    lstm_model.compile(optimizer=SGD(learning_rate=0.01, decay=1e-7, momentum=0.9, nesterov=False), loss='mean_squared_error')
    
    # 모델 학습
    lstm_model.fit(x_train, y_train, epochs=epochs, batch_size=batch_size, verbose=0, shuffle=False)
    
    return lstm_model
```

- lstm_arch 함수는 LSTM 모델을 생성하고 학습시키는 역할

**lstm_arch 함수 상세 분석**

```python
    # 모델 구성 (LSTM 레이어 2개, 활성화함수: 하이퍼볼릭탄젠트 사용)
    lstm_model = Sequential([
        LSTM(units=50, return_sequences=True, input_shape=(x_train.shape[1], 1), activation='tanh'),
        LSTM(units=50, activation='tanh'),
        Dense(units=periods) 
    ])
```

- 레이어를 선형으로 쌓은 구조를 갖는 Sequential 모델 생성
- 첫 번째 LSTM 레이어를 추가
    - units 매개변수는 LSTM 레이어의 뉴런 수를 나타냄
    - return_sequences=True로 설정하면 LSTM 레이어가 각 시간 step에서 출력을 반환
    - input_shape는 입력 데이터의 모양
        - x_train.shape[1]은 시간 창의 길이
    - 위 LSTM 개념에서 언급했듯이 활성화 함수는 tanh 사용
- 두 번째 LSTM 레이어
    - return_sequences 설정하지 않았으므로 마지막 시간 step에서만 출력 반환
- Dense 레이어
    - Dense 레이어는 출력 레이어로 units=periods로 설정되어 있어서 모델은 periods 크기의 출력을 생성
    

```python
# 모델 컴파일 (optimizer : SGD, 손실함수: MSE 사용)
    lstm_model.compile(optimizer=SGD(learning_rate=0.01, decay=1e-7, momentum=0.9, nesterov=False), loss='mean_squared_error')
```

- 최적화 알고리즘
    - SGD(확률적 경사 하강법) 사용
- Hyper parameter 설정
- loss 변수는 손실 함수를 의미하며 MSE(평균 제곱 오차)를 사용

```python
# 모델 학습
    lstm_model.fit(x_train, y_train, epochs=epochs, batch_size=batch_size, verbose=0, shuffle=False)
```

- 생성한 데이터셋 기반으로 모델 학습을 진행
- epochs : 전체 데이터셋 반복 횟수
- batch_size : 한 번에 모델이 처리할 데이터 샘플 갯수(건너 뛰는 step으로 생각)
- verbose = 0 : 학습 과정을 출력 x
- shuffle=False : 데이터를 섞지 않음

최종적으로 lstm_model을 반환하며, 이는 성능 평가 함수에서 이용된다.

### 모델 성능 평가

```python
# 모델 성능 평가
def lstm_performance(lstm_model, sc, x_test, test, epochs, batch_size):
    # 예측
    preds = lstm_model.predict(x_test)
    # 원래 값으로 변환
    preds = sc.inverse_transform(preds)
    
    # 실제값과 예측값을 비교하기 위한 데이터프레임 생성
    predictions_plot = pd.DataFrame(columns=['actual', 'prediction'])
    predictions_plot['actual'] = test.iloc[0:len(preds), 0]
    predictions_plot['prediction'] = preds[:, 0]
    
    # RMSE 계산
    mse = MeanSquaredError()
    mse.update_state(np.array(predictions_plot['actual']), np.array(predictions_plot['prediction']))
    RMSE = np.sqrt(mse.result().numpy())
    
    # 그래프
    return (predictions_plot.plot(figsize=(15, 5), 
                                title=f'lstm performance\nepochs={epochs}, batch size={str(batch_size)}, RMSE={str(round(RMSE, 4))}'))
```

**예측**

- 학습된 모델을 사용하여 x_test에 대한 예측값 생성
- 해당 예측값은 스케일링이 적용된 상태이므로 `sc.inverse_transform` 을 사용하여 원래 데이터의 단위로 변환

**성능 평가**

- 실제값(actual)과 예측값(prediction)을 비교하기 위한 Dataframe 생성
- RMSE(평균 제곱근 오차)를 사용하여 실제값과 예측값 차이 확인(손실함수)
    - 모델 생성 부분에서의 손실함수인 MSE는 최적화 단계에서의 모델의 예측값과 실제값 간의 차이를 측정하여 최소화하기 위해 사용

**그래프**

- lstm_performance 함수의 반환값으로 예측값과 실제값을 비교하는 그래프(시각적)를 생성

### 스케일러, 모델, 그래프 저장

최종적으로 얻은 결과물들을 설정한 경로에 저장하는 함수이다.

```python
def save_output(sc, lstm_model, plot):
    # 출력 폴더 생성
    output_path = './Output/Learning_lstm'
    os.makedirs(output_path,exist_ok=True)

    dump(sc, f'{output_path}/scaler.pkl') # scaler 저장
    lstm_model.save(f'{output_path}/lstm_model.h5') # 모델 저장
    plt.savefig(f'{output_path}/lstm_performance_graph.tiff') # 그래프 저장
```

### 기본값 실행

```python
def training(window_size, periods):
    # 베스트 모델의 하이퍼 파라미터 사용
    epochs = 700
    batch_size = 32

    # 데이터 읽어오기
    filename = './Output/Data_preprocessing/preprocessed.csv'
    df = read_data(filename)
    
    # 학습 데이터 / 테스트 데이터 분할
    train, test = train_test_split(df)

    # 데이터 스케일링
    sc = data_scaling(train)

    #  x_train, y_train, x_test 생성
    x_train, y_train = create_train(train,window_size, periods, sc)
    x_test = create_x_test(test,window_size, sc)

    # 모델 생성
    lstm_model = lstm_arch(x_train, y_train, periods, epochs, batch_size)

    # 모델 성능 평가
    plot = lstm_performance(lstm_model, sc, x_test, test, epochs, batch_size)

    # 스케일러, 모델, 그래프 저장
    save_output(sc, lstm_model, plot)

```

- `-l` 옵션을 통해 기본값(hyper parameter)으로 실행 가능한 코드

---

## 3_Prediction.py

`1_Preprocessing_tool.py`과 `2_Learning_LSTM.py` 을 통해 데이터 전처리 후 해당 데이터셋으로 LSTM 모델을 학습 시키는 과정을 진행했다. 이후 학습된 모델을 기반으로 실제 데이터를 넣어서 예측(Prediction)을 수행해야하는 데 해당 스크립트에서 이를 진행한다.

`-a` 옵션을 사용하지 않고 custom하여 예측을 진행할 경우 전처리 ~ 예측(입력 데이터에 대한 예측값 생성)

### **arguments**

- -h : parse_arguments()의 인자들에 대한 설명 출력(help 기능)
- -f : 전처리한 파일 이름을 입력(./Input/sample.csv)
- -c : 원본 데이터의 통계 파일 이름 입력(criteria.csv)
- -dp : 데이터 전처리를 실행
    - 기본은 결측치 보정
    - 도구 상태가 -p(--prediction)이면 하루 간격으로 시간을 병합
- -t : -dp와 함께 사용하는 옵션으로 데이터의 시간 간격을 변경 및 선택
- -w : -dp와 함께 사용하는 옵션으로 주말 또는 평일 데이터 구하기
- -p : 도구를 예측 상태로 설정(예측에 대한 인자)
- -d : 도구를 이상 탐지 상태로 설정
- -a : 특정 값으로 이상탐지와 예측 수행(기본값 실행)

```python
def main():
    args = parse_arguments()

    # 이상탐지, 예측 
    if args.all:
        abnormal_detection.abnormal_detection(args.filename, args.criteria) # 이상탐지
        predict.prediction(args.filename, args.criteria) # 예측 
    else:
        # 데이터 읽어오기
        df = abnormal_detection.read_data(args.filename) 
    
        # 데이터 전처리 : 결측치 보정, 시간 간격 병합, 평일/주말 데이터
        if df.isnull().any().any():
            df = preprocessing.Missing(df) # 결측치 보정

        if args.data_preprocessing or args.prediction: # 시간 간격 병합
            time_interval = {'hourly': '1H', 'daily': '1D'}.get(args.time)
            df = preprocessing.TimeIntervalData(df, time_interval)

            # 평일 / 주말 데이터 구하기    
            if args.week in ['weekday', 'weekend']: 
                df = preprocessing.week(df, args.week)
        
        # 모델과 스케일러 불러오기
        sc, lstm_model = abnormal_detection.load_model_and_scaler()

        # 모델의 윈도우 사이즈 찾기
        window_size = lstm_model.layers[0].input_shape[1]
    
        # x_data 생성
        x_data = abnormal_detection.create_x_new_data(df, window_size, sc)

        # 예측
        preds = abnormal_detection.predictions(x_data, lstm_model, sc)

        # 이상 탐지
        if args.detection:
            # 예측값에 대한 시계열 데이터 생성
            preds_df = abnormal_detection.create_time_series_data(df, preds)

            # 이상치 추출
            abnormal_df = abnormal_detection.detection(preds_df, args.criteria)
    
            # 이상치 데이터 저장
            abnormal_detection.save_data(abnormal_df)       

        # 예측
        if args.prediction: 
            # 예측값에 대한 시계열 데이터 생성
            periods_df = predict.create_predictive_data(df, preds)

            # 이상치 검출
            abnormal_df = abnormal_detection.detection(pd.DataFrame(periods_df.iloc[:,0]), args.criteria)

            # 레이블 채우기
            periods_df = predict.fill_label(periods_df, abnormal_df)

            # 예측 데이터 저장
            predict.save_data(periods_df)

```

- 초기 if 조건문은 `-a` 옵션을 사용할 경우 사전에 정의한 기본값으로 이상탐지 및 예측을 진행
- else 구문의 함수들은 `Abnormal_detection.py` 과 `Training.py` 로 설명

---

## Abnormal_detection.py

해당 스크립트는 기존 Data_preprocessing.py 흐름과 유사한 부분이 존재하여 코드 내에서 다른 부분만 언급 및 작성 

### 순서

1. 데이터 읽어오기(Raw data)
2. 결측치 보정
3. **모델과 스케일러 불러오기**
4. **x_data 생성**
5. 예측
6. 예측값에 대한 시계열 데이터 생성
7. 이상치 검출
8. 이상치 데이터 저장
    1. ./Output/Prediction/abnormal.csv

### Import

```python
import importlib
preprocessing = importlib.import_module('Data_preprocessing')
training = importlib.import_module('Training')
from keras.models import load_model
from joblib import load
import pandas as pd
import numpy as np
import sys
import os 
```

위에서 설명하지 않은 라이브러리 설명

- from keras.models import load_model : 이전 과정에서 학습한 LSTM 모델을 불러오기
    - 모델 저장 파일 형식 : h5
- from joblib import load : 이전 과정에서 얻은 스케일러 불러오기
    - 스케일러 저장 파일 형식 : pkl(pickle)

### 데이터 읽어오기

```python
def read_data(file_name):
    df = pd.read_csv(file_name, index_col = 0) 

    # 데이터프레임 인덱스를 데이트타임인덱스로 변환
    df.index = pd.to_datetime(df.index)
    df.index.name = 'time'

    # values 이름 추출
    col = df.columns[0]

    # float 변환
    df[col] = pd.to_numeric(df[col], errors='coerce') 
    df[col] = df[col].astype(float)
    
    # 인덱스 정렬
    df = df.sort_index(ascending=True) 
    return df
```

- read_data(file_name) 함수는 동일하므로 설명 생략

### 모델과 스케일러 불러오기

```python
def load_model_and_scaler():
    # 스케일러 불러오기
    sc = load('./Output/Learning_lstm/scaler.pkl')

    # 모델 불러오기 
    lstm_model = load_model('./Output/Learning_lstm/lstm_model.h5')

    return sc, lstm_model
```

- 이전 과정에서 학습한 LSTM 모델 및 스케일러 불러오기

### x_data 생성

```python
def create_x_new_data(new_data, window_size, sc):
    data = new_data.values
    data_len = len(data)
    
    # 학습 데이터 스케일링
    data_scaled = sc.transform(data)
    
    # x 학습데이터 생성
    x_data = []

    for i in range(data_len - window_size):
        x_data_end = i+window_size 
        x_data.append(data_scaled[i:x_data_end, 0])
 
    # 리스트를 넘파이 배열로 변환
    x_data =  np.array(x_data)

    # x_data를 텐서로 변환
    x_data = np.reshape(x_data, (x_data.shape[0], x_data.shape[1], 1))
    
    return x_data
```

- create_x_new_data(new_data, window_size, sc) 함수는 동일하므로 설명 생략

### 예측하기

```python
def predictions(x_data, lstm_model, sc):
    # 예측
    preds = lstm_model.predict(x_data)
    # 원래 값으로 변환
    preds = sc.inverse_transform(preds)
    return preds
```

- predictions(x_data, lstm_model, sc) 함수는 동일하므로 설명 생략

### 예측값에 대한 시계열 데이터 생성

```python
# 예측값에 대한 시계열 데이터 생성
def create_time_series_data(df, preds):
    # values 이름 추출
    col = df.columns[0]

    # 예측값에 대한 시계열 데이터 생성
    preds_df = pd.DataFrame(columns=[col],
                            index=(df.loc[:, col][0:len(preds)]).index)
    preds_df[col] = preds[:, 0]

    return preds_df
```

- 시계열 데이터 생성
    - 주어진 Dataframe의 첫 번째 컬럼에 예측값을 채워서 새로운 Dataframe 생성
    - 이때 예측값은 이전 데이터의 시간과 일치해야 하므로, 예측값의 길이 만큼을 사용하여 인덱스 생성
- 예측값에 대한 시계열 데이터를 생성하는 이유는 이상치 검출 분석에 활용될 수 있음

### 이상치 검출

```python
def detection(preds_df, criteria):
    # 학습 데이터의 통계표 읽어오기
    table = pd.read_csv(criteria, index_col = 0) 
    
    # 열 추출
    column_values = preds_df.iloc[:,0]

    # 이상치 데이터 생성
    if all(idx in table.index for idx in ['U_level', 'L_level']): # U_level와 L_level가 있는 경우
        U_level = table.loc['U_level']['Values'] # upper limit 
        L_level = table.loc['L_level']['Values'] # lower limit 
        abnormal_df = preds_df[(column_values <= L_level) | (column_values >= U_level)]
    
    elif 'U_level' in table.index: # U_level만 있는 경우
        U_level = table.loc['U_level']['Values']
        abnormal_df = preds_df[column_values >= U_level]
    
    elif 'L_level' in table.index: # L_level만 있는 경우
        L_level = table.loc['L_level']['Values'] 
        abnormal_df = preds_df[column_values <= L_level]
    
    
    if  abnormal_df.empty:
        print('이상치가 없습니다.')
    
    return abnormal_df
```

- Data_processing.py에서 작성한 Anomalous 함수(이상치 보정)과 유사 함수
- 기존과 다른 점은 이상치 데이터를 생성한 후 새로운 Dataframe에 저장
- 이상치가 없는 경우 “이상치가 없습니다” 출력
- 이상치가 존재할 경우 이상치를 담은 Dataframe인 abnormal_df 반환

### 이상치 데이터 저장

```python
def save_data(abnormal_df):
    # 폴더 생성
    output_path = './Output/Prediction'
    os.makedirs(output_path, exist_ok=True)
     
    # 이상치 데이터 저장
    abnormal_df.to_csv(f'{output_path}/abnomal.csv')
```

- 이상치 데이터를 해당 경로에 저장

### 기본값 실행

```python
def abnormal_detection(file_name,criteria):
    # 파일 읽어오기
    df = read_data(file_name)

    # 데이터 전처리: 결측치 처리
    if df.isnull().any().any():
        df = preprocessing.Missing(df)

    # 모델과 스케일러 불러오기
    sc, lstm_model = load_model_and_scaler()

    # 모델의 윈도우 사이즈 찾기
    window_size = lstm_model.layers[0].input_shape[1]
    
    # x_data 생성
    x_data = create_x_new_data(df, window_size, sc)

    # 예측
    preds = predictions(x_data, lstm_model, sc)

    # 예측값에 대한 시계열 데이터 생성
    preds_df = create_time_series_data(df, preds)

    # 이상치 추출
    abnormal_df = detection(preds_df, criteria)
    
    # 이상치 데이터 저장
    save_data(abnormal_df)
```

- abnormal_detection(file_name, criteria) : `-a` 옵션을 사용하여 기본값으로 실행하는 함수

---

## Prediction.py

이상 탐지(Abnormal_detection.py에 정의) 후 예측 과정을 수행한다. 

- 3_Prediction.py 예측 코드 흐름

```
        if args.prediction: 
            # 예측값에 대한 시계열 데이터 생성
            periods_df = predict.create_predictive_data(df, preds)

            # 이상치 검출
            abnormal_df = abnormal_detection.detection(pd.DataFrame(periods_df.iloc[:,0]), args.criteria)

            # 레이블 채우기
            periods_df = predict.fill_label(periods_df, abnormal_df)

            # 예측 데이터 저장
            predict.save_data(periods_df)
```

- Abnormal_detection.py의 detection 함수를 이용한 이상치 검출 부분이 있는 이유는 생성된 예측값에 대한 시계열 데이터(periods_df)를 사용하여 이상치를 검출하는 데 이때 사용, 이후 Dataframe 반환

### 예측 데이터 생성

```python
def create_predictive_data(df, preds):
    col = df.columns[0]
    last_index = df.index[-1] # # 데이터의 마지막 인덱스 찾기
    periods = preds.shape[1] # # prediction window size 찾기
    freq = pd.infer_freq(df.index) # 시간 간격 찾기

    # 데이트타임 생성
    preds_index = pd.date_range(str(last_index), periods=(periods+1), freq=freq)
    preds_index = preds_index[1:] # 예측값의 데이트타임 추출

    # 예측값의 시계열 데이터 생성
    periods_df = pd.DataFrame(index=preds_index, columns=[col, 'label'])
    periods_df[col] = list(preds[-1])
    periods_df.index.name =  'time'

    return periods_df
```

- 기존 df와 예측값 pred를 이용하여 예측값을 포함한 Dataframe인 periods_df 생성하고 이를 반환

### 레이블 채우기

```python
def fill_label(periods_df, abnormal_df):
    col = periods_df.columns[0]
    # 예측 데이터와 이상치 데이터의 인덱스에서 교집합 추출
    common_index = periods_df.index.intersection(abnormal_df.index)
    # label 채우기
    periods_df.loc[common_index,'label'] = 'Abnormal' # 교집합: Abnormal
    periods_df['label'].fillna('Normal', inplace=True) # 아니면 :Normal

    for index, row in periods_df.iterrows():
        print(f'\n시간: {index} - 예측 값: {row[col]}, 레이블: {row["label"]}')

    return periods_df
```

- 예측값에 대한 시계열 데이터(periods_df)와 이상치를 포함하는 Dataframe인 abnormal_df를 인수로 받아서 레이블을 채우는 함수
- 두 개의 Dataframe의 index를 교집합으로 하여 추출하는데, 이 과정을 통해 이상치가 예측값의 어느 부분에 위치해있는지를 파악 가능
- 즉, abnormal_df는 이상치가 존재하는 특정 시간을 인덱스로 하는 Dataframe이므로 periods_df 의 인덱스에서 abnormal_df의 인덱스와 동일하다면 `Abnormal` 로 표시하고 아니라면 `Normal` 로 표시
(label 속성에 값 표시)

### 예측 데이터 저장

```python
def save_data(periods_df):
    # 출력 폴더 생성
    output_path = './Output/Prediction'
    os.makedirs(output_path,exist_ok=True)

    # 예측한 데이터 저장
    periods_df.to_csv(f'{output_path}/prediction.csv')
```

- 위 과정에서 label 속성에서 이상치까지 라벨링한 결과물을 설정한 경로에 저장

### 기본값 실행

```python
def prediction(file_name, criteria):
    # 데이터 읽어오기
    df = read_data(file_name)
    # 데이터 전처리: 결측치 처리, 시간 간격으로 병합
    if df.isnull().any().any():
        df = preprocessing.Missing(df)
    df = preprocessing.TimeIntervalData(df, '1D') # 1시간 간격으로 병합 

    # 모델과 스케일러 불러오기
    sc, lstm_model = abnormal_detection.load_model_and_scaler()

    # 모델의 윈도우 사이즈 찾기
    window_size = lstm_model.layers[0].input_shape[1]
    
    # x_data 생성
    x_data = abnormal_detection.create_x_new_data(df, window_size, sc)

    # 예측
    preds = abnormal_detection.predictions(x_data, lstm_model, sc)

    # 예측값에 대한 시계열 데이터 생성
    periods_df = create_predictive_data(df, preds)

    # 이상치 검출
    abnormal_df = abnormal_detection.detection(pd.DataFrame(periods_df.iloc[:,0]), criteria)

    # 레이블 채우기s
    periods_df = fill_label(periods_df, abnormal_df)

    # 예측 데이터 저장
    save_data(periods_df)
```