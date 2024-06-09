# 업무내용

- 논의사항 정리
- 데이터셋 분리 확인 : 기존 방식인 개수 파악이 아닌 파일을 생성하여 실제로 분할 데이터셋 확인
- EDA 추가 : 분석에 필요한 추가적인 시각화 진행
- 프로젝트 아키텍처 설정 및 체크리스트 작성
    - ETL 작업
    - model 실행
    - 결과값 전송
- LSTM 알고리즘 Scale 조정 : 0 ~ 1000(그래프로 이해하기 쉽게)
<br/><br/>

## 6/3

### 논의사항

**LSTM Algorithm**

- 옵션 설정
    - 데이터 저장 :장소마다 환경이 다르기 때문에 3, 6, 9개월 설정 필요
        - 최소 3개월 이상(best : 1 year)
    - 데이터 처리 단위 : 최소 분 단위 (best : 1 min, 10 min)
- 예측
    - 의미있는 예측 : 1 day, 1 week, 1 month
- 이상 징후
    - 관심
    - 주의
    - 경계
    - 심각
    - 4단계의 범위는 아직 미정
- 추가적인 알고리즘 구현
    - 어느 시간 대가 가장 저유량인지 파악
    - Ex) 야간 최소유량 파악(최솟값 찾기)
    - 설정한 경계값이 넘어가면 이상치 알림

- 데이터 저장 :장소마다 환경이 다르기 때문에 3, 6, 9개월 설정 필요
    - 최소 3개월 이상(best : 1 year)
- 데이터 처리 단위 : 최소 분 단위 (best : 1 min, 10 min)

**System Architecture**

- 프로젝트의 구조 설정
    - ETL 작업
    - model 실행
    - 결과값 전달
- check list
    - 체크리스트를 통해 해당 기능은 어떤 회사가 진행해야하는 지 파악

### 데이터셋 분리 확인

**설명**

기존에는 학습 데이터와 테스트 데이터를 print()문을 통해 개수로만 확인하였지만, 실제로 잘 나누어져있는지 확인하기 위해 각 데이터들을 csv파일 형식으로 저장하여 확인

```python
# 학습 데이터 / 테스트 데이터 분할 (7:3)
def train_test_split(df):
    train_size = int(0.7 * len(df))
    train = df.iloc[:train_size]
    test = df.iloc[train_size:]

    # 학습 데이터 / 테스트 데이터 확인을 위한 저장
    train.to_csv('./Check/check_train_data.csv')
    test.to_csv('./Check/check_test_data.csv')

    # 데이터 분리 결과 출력
    print(f"Train data Size: {len(train)} rows")
    print(f"Test data Size: {len(test)} rows")

    return train, test
```

Check 디렉토리를 생성하여 학습 / 테스트 데이터를 저장

- check_train_data.csv

![week6_01](https://github.com/Kyeong6/whatever/assets/100195725/361a3e9c-b5ca-47b0-8401-c6cc1e12794e)


- check_test_data.csv

![week6_02](https://github.com/Kyeong6/whatever/assets/100195725/13dbd539-3311-42e4-aae7-972d987f18f5)


- terminal 출력

![week6_03](https://github.com/Kyeong6/whatever/assets/100195725/5127c0b8-2e4f-4562-adbf-4ade07dd3b58)


문제없이 데이터셋이 분할되고 있음을 알 수 있다.
</br><br/>

## 6/5

**설명**

본 프로젝트는 LSTM 알고리즘을 통해 최종적 이상치의 유무를 파악한다.  
프로젝트를 진행하기 위해서 아키텍처를 구성하고 체크리스트를 작성하여 자문에서의 질문 사항을 정리한다.    

프로젝트의 간단한 플로우는 다음과 같다.  
- 데이터 적재
- ETL 작업
- Model 실행
- 결과값 전송
  </br><br/>

**1. Raw Data 받기**  
기기에서 얻은 Raw Data를 받는 단계로써 해당 과정은 자문이 필요하다

**2. Raw Data를 DB에 적재(Load)**  
기기에서 얻은 Raw Data를 DB에 적재하여 csv 파일로 변환할 준비를 한다.

**3. DB의 값들을 csv 파일로 변환(Extract)**  
DB의 값들을 추출하여 csv 파일 형식으로 변환한다. 왜냐하면 현재 LSTM 모델은 Input을 csv 파일 형식으로 설정되어있기 때문이다.

**4. csv 파일의 값을 변형하여 Input 디렉토리에 배치(Transform)**  
csv 파일의 값들을 모델의 Input으로 설정한 구조로 변형(pandas 이용)하여 Input 디렉토리에 배치하여 예측을 수행할 준비를 완료한다.

**5. 3_Prediction.py 실행**  
1_Preprocessing_tool.py와 2_Learning_LSTM.py는 모델을 학습할 때 진행하는 코드로, 최종적인 제품 단계에서는 이미 학습된 모델을 사용하여 예측을 수행하므로 기존에 h5, sclaer 파일이 사전에 존재한다. 따라서 3_Prediction.py 파일만 실행한다.

**6. 예측값을 얻은 뒤 적재 혹은 알림 구현**  
예측값을 얻은 뒤 제품의 목적에 따라 적재 혹은 알림을 구현해야하는데, 이는 자문이 필요하다.   

**7. 위의 단계를 수행하는 자동화 시스템 구축**  
1 ~ 6번까지의 단계가 1 cycle이다. 정해진 시간에 위의 단계를 수행하는 자동화 시스템을 구축해야 한다.
</br><br/>

## 6/6

**설명**

수행해야 할 업무는 다음과 같다.

- LSTM 모델에 옵션을 주어 5, 10분 단위로 학습
    - 이미지 상에서 꺾이는 점이 더 많이 나오는 형태의 그래프 구현
    - 개선된 형태의 다른 형태의 그래프도 그릴 수 있으면 추가로 진행
    - 최종적으로 타사의 xgboost 모델과의 예측값 비교
</br><br/>

**데이터 전처리**

제공받은 데이터셋(TN, TOC)의 구조는 다음과 같다. 

_time_gateway Sensor_S4_TN_9h

9/1/22 0:00, 8.00

9/1/22 0:10, 7.97

9/1/22 0:20, 8.25

위의 구조를 데이터 전처리 과정을 수행할 수 있게 변환 과정을 진행하였다. 
</br><br/>

- _time_gateway 열의 값을 YYYY/MM/DD HH:MM 형식으로 변환

```python
# 날짜 형식 변환 함수
def convert_date_format(date_str):
    return pd.to_datetime(date_str, format='%m/%d/%y %H:%M').\
    strftime('%Y/%m/%d %H:%M')
    
# 날짜 형식 변환 적용
tn['_time_gateway'] = tn['_time_gateway'].apply(convert_date_format)
```
</br><br/>

- 데이터셋 분리

```python
# tn 학습 데이터 생성
tn_train = tn.iloc[0:29888]

# tn 예측 데이터 생성
tn_predict = tn.iloc[29888:]

# 분석을 위한 데이터셋 저장
tn_train.to_csv(save_path+"LSTM_pipeline/Input/tn_train.csv",index=False)
tn_predict.to_csv(save_path+"LSTM_pipeline/Input/tn_predict.csv",index=False)
```

학습 / 예측 데이터를 나눈 뒤 Input 디렉토리에 저장하였다.
</br><br/>

## 1. TN 데이터셋 진행

### **1_Preprocessing_tool.py**

10분 간격으로 데이터 전처리를 하는 것이 목표이기 때문에 코드를 수정하였는데, 다음과 같다.

```python
parser.add_argument('-t', '--time', choices=['min', 'hourly', 'daily'], \
help='데이터의 시간 간격을 변경합니다. min, hour, day 중에서 선택할 수 있습니다.') 
```

```python
if args.time is not None: 
    # 1시간 간격 병합
    # time_interval = {'hourly': '1H', 'daily': '1D'}.get(args.time)
            
    # 10분 간격 병합
    time_interval = {'min': '10T','hourly': '1H', 'daily': '1D'}.get(args.time)
    df = preprocessing.TimeIntervalData(df,time_interval)
```

기존에 1시간 간격의 병합에서 10분 간격의 병합으로 수정하였다.
</br><br/>

### **Data_preprocessing.py**

-p 옵션을 통해 기본값으로 데이터 전처리를 실행한다. 명령어를 편하게 사용하기 위해 기본값 또한 수정하였다. 

```python
def Data_preprocessing(file_name, percent):
    
    # 데이터 읽어오기
    df = read_data(file_name)

    # 결측치 보정
    df = Missing(df)

    # # 데이터 병합 (1D)
    # time_interval = '1D'

    # 데이터 병합 (10T)
    time_interval = '10T'
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

기존에 데이터 병합 (1D)에서 데이터 병합 (10T)로 기본값을 수정하였다. 
</br><br/>

**명령어**

```bash
python 1_Preprocessing_tool.py -f ./Input/tn_train.csv -p
```
</br><br/>

**결과**

1. creteria.csv와 preprocessed.csv를 확인해본결과 잘 적용되었음을 확인하였다.
</br><br/>

![tn1](https://github.com/Kyeong6/whatever/assets/100195725/e238bd3e-5a08-432e-8141-9a3170331116)
</br><br/>

2. 수행 시간 및 cpu / memory 사용량은 다음과 같다.

```bash
 3.9442 sec
cpu usage               : 100 %
memory usage            : 0.07 GB
```

기존 데이터셋이 10분 간격으로 되어있기 때문에 병합하는 과정이 짧았다.
</br><br/>

### 2_Learning_LSTM.py

학습 코드는 기존과 동일하다.

**명령어**

```bash
python 2_Learning_LSTM.py -l
```
</br><br/>

**결과**

![tn2](https://github.com/Kyeong6/whatever/assets/100195725/b225e9f4-67b3-44a0-bcd9-22dcb4086e15)
</br><br/>

```bash
Train data Size: 21369 rows
Test data Size: 9159 rows
Graph Analysis:
X-axis: Time with 9152 points
Y-axis: Values ranging from 4.279999999999998 to 19.91

Prediction Statistics:
Mean Actual Value: 16.14129042832168
Mean Predicted Value: 15.804547309875488
Variance of Actual Values: 16.478266206976446
Variance of Predicted Values: 14.542067527770996
RMSE: 0.6800000071525574

Residuals Analysis:
Mean Residual: 0.3367407080531112
Variance of Residuals: 0.3490071184325513
Min Residual: -11.668686599731444
Max Residual: 12.43568124771118

Number of Outliers: 68
Outliers:
time
2023-02-01 04:10:00    2.128493
2023-02-01 04:20:00    2.750809
2023-02-01 04:30:00    1.987365
2023-02-01 05:10:00   -6.248434
2023-02-01 05:20:00   -2.405458
                         ...   
2023-03-28 04:50:00   -9.288620
2023-03-28 05:00:00   -9.520677
2023-03-28 05:10:00   -9.326534
2023-03-29 09:40:00   -1.799419
2023-03-31 02:00:00    1.567230
Length: 68, dtype: float64
 1143.0210 sec
cpu usage               : 75.8 %
memory usage            : 1.1 GB
```

**비용**

- 모델을 학습하는 데 약 19분 정도가 소요됐다.
</br><br/>

**그래프 분석**

- 실제 값(파란색)과 예측 값(주황색)이 비교적 잘 맞아떨어지나, 특정 구간에서는 큰 차이가 보인다.
- 일부 기간에서 값이 급격히 변하는 부분이 있으며, 예측 모델이 이 변화를 잘 포착하지 못한 것으로 보인다.
- 그래프에서 몇몇 값이 정상 범위를 벗어나 이상치가 존재함을 알 수 있다.
</br><br/>

**통계 분석**

- **Root Mean Squared Error(RMSE)**: 0.68
- **Prediction Statistics:**
    - 실제 값의 평균: 16.14
    - 예측 값의 평균: 15.80
    - 실제 값의 분산: 16.48
    - 예측 값의 분산: 14.54
- **Residuals Analysis:**
    - 평균 잔차: 0.34
    - 잔차의 분산: 0.35
    - 최소 잔차: -11.67
    - 최대 잔차: 12.44
- **Outliers**:
    - 68개의 이상치
</br><br/>

**결론**

RMSE 값이 낮아 비교적 괜찮은 성능이라 할 수 있지만, 이상치가 발견된 부분의 제거 등 추가 분석이 필요하다.

또한, 데이터의 급격한 변화가 있는 구간에 대해 모델이 잘 대응할 수 있도록 추가적인 작업이 필요하다.
</br><br/>

### 3_Prediction.py

tn_train.csv를 통해 학습을 진행하였고, 예측은 tn_predict.csv를 통해 진행한다.

**명령어**

```bash
python 3_Prediction.py -f ./Input/tn_predict.csv -a
```

3_Prediction.py에서 사용하는 Abnormal_detection.py, Prediction.py파일의 수정은 학습한 후 저장한 요소들을 불러와서 실행하기 때문에 필요하지 않다.
</br><br/>

**결과**

```bash
시간: 2023-09-01 00:00:00 - 예측 값: 8.12365436553955
레이블: Normal
 7.0806 sec
cpu usage               : 113.7 %
memory usage            : 0.4 GB
```
</br><br/>

## 2. TOC 데이터셋 진행

TOC 데이터셋은 toc_train.csv, toc_predict.csv이다. 

해당 부분에서는 과적합을 확인하는 코드를 추가하여 진행하였다.
</br><br/>

### 변경사항

val 변수를 생성하여 Training.py의 모든 부분에 추가하였다. 

```python
# 학습 곡선 생성 및 저장
def plot_learning_curves(history):
    plt.figure(figsize=(15, 5))
    plt.plot(history.history['loss'], label='Training Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')
    plt.title('Training and Validation Loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()
    output_path = './Output/Loss_history'
    os.makedirs(output_path, exist_ok=True)
    plt.savefig(f'{output_path}/learning_curves.tiff', format='tiff')
    plt.show()

    # 학습 손실 및 검증 손실을 CSV 파일로 저장
    loss_history = pd.DataFrame({
        'epoch': range(1, len(history.history['loss']) + 1),
        'loss': history.history['loss'],
        'val_loss': history.history['val_loss']
    })
    loss_history.to_csv(f'{output_path}/loss_history.csv', index=False)

```

크게 달라진 점은 plot_learning_curves() 함수를 통해 loss에 관한 그래프와 정보를 따로 저장했다.

Training.py를 참조하고 있는 2_Learning_LSTM.py 또한 Training.py에 맞게 인자를 추가 및 수정했다.

### 1_Preprocessing_tool.py

**명령어**

```bash
python 1_Preprocessing_tool.py -f ./Input/toc_train.csv -p
```
</br><br/>
**결과**

```python
 3.5627 sec
cpu usage               : 98.2 %
memory usage            : 0.07 GB
```
</br><br/>

### 2_Learning_LSTM.py

**명령어**

```bash
python 2_Learning_LSTM.py -l
```

**결과**

![toc1](https://github.com/Kyeong6/whatever/assets/100195725/c4f77e61-26ea-4de8-86b8-b8b0371042c5)
</br><br/>

![toc2](https://github.com/Kyeong6/whatever/assets/100195725/3070306c-e718-4e69-8225-d1808e3d65b6)
</br><br/>

```python
Train data Size: 24422 rows
Validation data Size: 3052 rows
Test data Size: 3054 rows
2024-06-06 23:38:14.871857: W tensorflow/core/platform/profile_utils/cpu_utils.cc:128] Failed to get CPU frequency: 0 Hz
96/96 [==============================] - 0s 856us/step
Graph Analysis:
X-axis: Time with 3047 points
Y-axis: Values ranging from 2.85 to 11.3

Prediction Statistics:
Mean Actual Value: 9.806383327863472
Mean Predicted Value: 9.794512748718262
Variance of Actual Values: 0.43513898367467346
Variance of Predicted Values: 0.377772718667984
RMSE: 0.3456000089645386

Residuals Analysis:
Mean Residual: 0.011871611301258125
Variance of Residuals: 0.11930959752495714
Min Residual: -7.060934448242188
Max Residual: 6.297203779220581

Number of Outliers: 18
Outliers:
time
2023-03-20 02:10:00    2.888031
2023-03-20 02:20:00    4.980553
2023-03-20 02:30:00    6.297204
2023-03-20 02:40:00    4.263176
2023-03-20 02:50:00    2.296371
2023-03-20 03:00:00    0.996465
2023-03-20 03:10:00   -6.864417
2023-03-20 03:20:00   -7.060934
2023-03-20 03:30:00   -7.006101
2023-03-28 03:50:00    1.680675
2023-03-28 04:00:00    3.271252
2023-03-28 04:10:00    3.891637
2023-03-28 04:20:00    2.541641
2023-03-28 04:30:00    1.311352
2023-03-28 04:50:00   -4.322994
2023-03-28 05:00:00   -5.033766
2023-03-28 05:10:00   -3.964880
2023-03-31 02:00:00    0.825565
dtype: float64
 1384.9398 sec
cpu usage               : 97.2 %
memory usage            : 1.04 GB
```

**그래프 분석**

현재 모델의 예측값과 실제값이 그래프와 RMSE값을 통해 매우 근접하다는 것을 알 수 있다.

또한 Training and Validation Loss 그래프를 확인해보면 유사하게 감소하고 있고, 두 값 모두 수렴하고 있다. 
이는 모델이 과적합되지 않았고, 학습이 안정적으로 진행되었음을 의미한다.
</br><br/>

**통계 분석**

- **Root Mean Squared Error(RMSE)**: 0.3456
- **Prediction Statistics:**
    - 실제 값의 평균: 9.8064
    - 예측 값의 평균: 9.7945
    - 실제 값의 분산: 0.4351
    - 예측 값의 분산: 0.3778
- **Residuals Analysis:**
    - 평균 잔차: 0.0119
    - 잔차의 분산: 0.1193
    - 최소 잔차: -7.0609
    - 최대 잔차: 6.2972
- **Outliers**:
    - 18개의 이상치
</br><br/>

**결론**

전체적으로 좋은 성능을 보이고, 예측값과 실제값이 잘 일치한다. 또한 학습과 검증 손실값이 잘 수렴하고 있어 과적합이 발생하지 않았음을 알 수 있다. 
</br><br/>

### 3_Prediction.py

**명령어**

```bash
python 3_Prediction.py -f ./Input/toc_predict.csv -a
```

**결과**

```bash
시간: 2023-09-01 00:00:00 - 예측 값: 5.970034599304199
레이블: Normal
 7.0601 sec
cpu usage               : 113.8 %
memory usage            : 0.4 GB
```
</br><br/>
## 추가적인 진행사항

**설명**

현재 3_Prediction.py를 실행하면 Output/Prediction/prediction.csv에 예측값이 저장이 된다.   
기존 코드를 실행하면 -f로 설정한 파일의 마지막 행만 확인한 후 예측을 진행하게 된다. (위의 결과 부분)   
xgboost와의 비교(시각화 이용)를 위해서는 특정 기간의 예측값들이 존재해야한다. 이를 위해서 기존 LSTM Pipeline 코드를 수정하였고, 최종적으로 실제값, xgboost의 예측값, LSTM의 예측값을 시각화하여 비교할 예정이다.
</br><br/>

### 코드 변경

**변경 사항**

[Kyeong6: whatever](https://github.com/Kyeong6/whatever/commit/b0efd067b29b38e4ea7f62971ffbf63a92a11a33)

window_size가 7로 설정되어 2023-03-31 22:50을 시작으로 하여 prediction.csv에는 2023-04-01 00:00부터 예측값을 존재하게 하였다. 
</br><br/>

**결과**

- 실행 시간 및 사용량확인

```bash
# TN
7189.5713 sec
cpu usage               : 83.3 %
memory usage            : 1.39 GB

# TOC
7331.8641 sec
cpu usage               : 94.6 %
memory usage            : 1.37 GB
```

2023-04-01 00:00 ~ 2023-08-31 23:50의 10분 간격 데이터(약 22,000개)를 예측하는 데 7189초
7331초로 2시간 정도의 시간이 소요됐다.
</br><br/>

- Ouput 확인(TOC)

![toc_result](https://github.com/Kyeong6/whatever/assets/100195725/a752b2fa-a329-4e34-bd80-a54c40754d5e)


prediction.csv와 abnormal.csv 모두 정상적으로 결과를 얻었음을 확인할 수 있다.
</br><br/>

### EDA

XGBoost와 LSTM 예측값을 TN / TOC 모두 확인한 후 python 라이브러리인 plotly로 시각화를 진행하였다.   
아래의 그래프를 확인해보면 LSTM이 XGBoost보다 실제값의 그래프와 유사하여 좋은 성능을 보임을 확인할 수 있다.
</br><br/>

**TN_XGBoost**

![tn_xgboost](https://github.com/Kyeong6/whatever/assets/100195725/0577ec4d-7b1e-4631-9661-c36914eeb671)
</br><br/>

**TN_LSTM**

![tn_lstm](https://github.com/Kyeong6/whatever/assets/100195725/09ad14d2-f240-4ca0-a706-8c848b8b1d91)
</br><br/>

**TN_Comparison**

![tn_comparison](https://github.com/Kyeong6/whatever/assets/100195725/5379966e-60e4-4f0e-8ce6-a4771cb2b3f8)
</br><br/>

**TOC_XGBoost**

![toc_xgboost](https://github.com/Kyeong6/whatever/assets/100195725/6e5d4615-1857-4aa5-8804-432b1b159570)
</br><br/>

**TOC_LSTM**

![toc_lstm](https://github.com/Kyeong6/whatever/assets/100195725/0b49bb47-39fa-43fe-b859-1e0817ebc663)
</br><br/>

**TOC_Comparison**

![toc_comparison](https://github.com/Kyeong6/whatever/assets/100195725/d91a3587-ad6a-48f8-9620-f48808295e49)
