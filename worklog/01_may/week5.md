# 업무 내용

1. 실데이터 전처리 : 원데이터를 LSTM에 사용하기 위한 전처리 진행
   
2. 실데이터 LSTM 사용 :기존에 사용하던 샘플 데이터가 아닌 실제 데이터 이용
   
3. 시간 측정 : time library를 이용한 작동시간 확인
   
4. CPU 및 MEM 사용량 확인 : os, psutil library를 이용한 cpu 및 memory 사용량 확인
   
5. 데이터셋 분리 확인 : train / test 분리가 잘 되었는지 확인
   
6. 그래프 분석 : tiff 파일 해석 및 분석 정보 terminal에 출력

## 5/27

### 실데이터 전처리

<img width="895" alt="week5_01" src="https://github.com/Kyeong6/whatever/assets/100195725/a082f718-ff57-4d9a-afca-8f1e11f6b987">


<img width="843" alt="week5_02" src="https://github.com/Kyeong6/whatever/assets/100195725/ca73b057-fa7f-4ea9-a9a9-a9fbb0e7d303">



**설명**

실데이터인 “정읍수도_순시유량.csv”를 전처리한 코드이다.

장명 배수지를 통해서 유입유량이 장명01, 02와 같은 블록으로 이동하므로 앞단에 존재하는 “장명배수지” 만 데이터 전처리를 수행하였다. 

### 실데이터 LSTM 사용

**실행 방법(기본값 실행)**

1. 1_Preprocessing_tool.py 

```bash
python 1_Preprocessing_tool.py -f ./Input/jangmyeong.csv -p
```

1. 2_Learning_LSTM.py

```bash
python 2_Learning_LSTM.py -l 
```

1. 3_Prediction.py

```bash
python 3_Prediction.py -f ./Input/jangmyeong.csv -a
```

**설명**

“정읍수도_순시유량.csv”를 전처리한 후 최종 행의 갯수는 5,271,041행이다. 

해당 데이터를 LSTM 실행한 결과 이상치가 존재하지 않았다.

![week5_03](https://github.com/Kyeong6/whatever/assets/100195725/2bfb0543-7626-46e8-8c5c-3853feceb42e)



## 5/30

### 시간 측정

**설명**

LSTM 모델을 작동하기 위해 실행되는 파일은 다음과 같다.

- 1_Preprocessing_tool.py
- 2_Learning_LSTM.py
- 3_Prediction.py

각각의 코드가 실행되는 시간을 파악하기 위해 time 라이브러리를 사용한다.

```python
import time

# 시간 측정 시작
start = time.time()

# 코드 생략
pass

# 종료와 함께 수행시간 출력
print(f"{time.time()-start: .4f} sec")
```

각 파일 별 실행시간은 다음과 같다. (두 번째 실행 스크린샷)

- 1_Preprocessing_tool.py

![week5_04](https://github.com/Kyeong6/whatever/assets/100195725/738b36f5-c99a-43a9-86ad-667e83c172c9)


→ 31.1337 sec

- 2_Learning_LSTM.py

![week5_05](https://github.com/Kyeong6/whatever/assets/100195725/0aa7efee-7234-4cda-a2be-5a9820af4229)


→ 17.6853 sec

- 3_Prediction.py

![week5_06](https://github.com/Kyeong6/whatever/assets/100195725/d2ec9a7e-27ef-4f64-8e1e-abd935ec0a04)


→ 18.2704 sec

총 시간은 67.0894 sec로 1분 7초 정도의 시간이 소요된다. 

위의 결과는 두 번째로 얻은 수행 시간으로 안정적인 수치를 얻기 위해 3번의 수행을 진행하였다.

- 첫 번째 실행
    - 1_Preprocessing_tool.py : 32.3325 sec
    - 2_Learning_LSTM.py : 27.52 sec
    - 3_Prediction.py : 18.2021 sec
    - 총 시간 : 78.0546 sec, 1분 18초
- 세 번째 실행
    - 1_Preprocessing_tool.py : 31.0973 sec
    - 2_Learning_LSTM.py : 17.0720 sec
    - 3_Prediction.py : 18.2689 sec
    - 총 시간 : 66.4382 sec, 1분 6초

세 번의 실행한 결과 2_Learning_LSTM.py에서 시간 차이를 보였다. 

시사하는 바는 2_Learning_LSTM.py에서 tiff(그래프 이미지)파일 등 Output을 얻으므로 첫 번째 실행 시간이 대략 10초 정도 시간이 더 소요되는 것을 알 수 있다. 

해당 프로젝트에서 두 번째, 세 번째 실행은 의미가 없으므로 첫 번째 실행이 기준이 되어야 한다. 

**결론**

5,271,041행, 약 5,000,000행의 LSTM 모델 소요시간은 대략 1분 18초이다.

### 사용량 확인

**설명**

각 파일들의 CPU 및 MEM 사용량 확인은 다음과 같이 코드를 작성하여 확인할 수 있다.

```python
import os
import psutil

# 현재 프로세스의 ID 가져오기
pid = os.getpid()
py = psutil.Process(pid)

# 코드 생략
pass

# CPU 및 MEM 사용량 출력
cpu_usage = os.popen("ps aux | grep " + str(pid) + " | grep -v grep | awk '{print $3}'").read().strip()
memory_usage = round(py.memory_info()[0] / 2.**30, 2)

print("cpu usage\t\t:", cpu_usage, "%")
print("memory usage\t\t:", memory_usage, "GB")
```

각 파일들의 CPU 및 MEM 사용량은 다음과 같다.

- 1_Preprocessing_tool.py

![week5_07](https://github.com/Kyeong6/whatever/assets/100195725/4f13f4ef-1b36-4a8c-a1f3-69b86134393b)


- 2_Learning_LSTM.py

![week5_08](https://github.com/Kyeong6/whatever/assets/100195725/241ca59c-35a5-4e8e-ae78-b4cb135ba98c)


- 3_Prediction.py

![week5_09](https://github.com/Kyeong6/whatever/assets/100195725/8bfe9731-0f84-4a20-b81d-dafc82ae03f4)


시간 측정 부분에서 언급했듯이 첫 번째 실행이 아닌 재실행이므로 2_Learning_LSTM.py의 사용량이 86.3%로 나왔지만 새로운 데이터를 첫 번째로 실행할 경우 90%가 넘을 것이라고 예상된다.

세 개의 파일은 많은 계산이 존재하여 CPU의 사용량이 90%가 넘는 것으로 확인된다. 

## 6/2

### 데이터셋 분리 확인

**설명**

학습 데이터와 테스트 데이터가 코드에 작성된 비율로 잘 분할되는 지 확인이 필요하여 추가적인 코드 작성을 하였다.

- Training.py

```python
def train_test_split(df):
    train_size = int(0.7 * len(df))
    train = df.iloc[:trainz_size]
    test = df.iloc[train_size:]
    
    # 추가 작성 : 데이터 분리 결과 출력
    print(f"Train data Size: {len(train)} rows")
    print(f"Test data Size: {len(test)} rows")
    
    return train, test
```

- 2_Learning_LSTM.py

```python
# 학습 데이터 / 테스트 데이터 분할
train, test = training.train_test_split(df)

# 추가 작성 : 학습 / 테스트 데이터 추가 확인
print("Train and Test data split done.")
print("Train data example:")
print(train.head())
print("Test data example:")
print(test.head())
```

위의 코드를 작성하여 얻은 출력은 다음과 같다.

![week5_10](https://github.com/Kyeong6/whatever/assets/100195725/99003012-c72d-4b8e-8327-d47930062413)


데이터셋 행의 총 개수인 367에 0.7을 곱하면 256이 나오므로 데이터셋이 잘 분리되고 있음을 알 수 있다.

### 그래프 분석

**설명**

tiff 파일로 그래프가 저장이 되는데, 이를 잘 파악하기 위해 그래프 설명과 추가적인 출력문장을 설정하였다.

<img width="850" alt="week5_11" src="https://github.com/Kyeong6/whatever/assets/100195725/f2437dc0-397a-4474-aaaa-3a4b084b3880">


<img width="850" alt="week5_12" src="https://github.com/Kyeong6/whatever/assets/100195725/4493ae7c-9fbe-4353-a9ec-791bdf47580c">


Training.py에서 위의 코드를 새롭게 작성한 부분은 다음과 같다.

- 그래프 생성 및 세부사항 출력
- 그래프에 대한 세부정보 출력
- 예측 결과 통계 출력
- 잔차 분석
- 이상치 확인

**그래프 생성 및 세부사항 출력**

범례를 통해 특정 그래프가 실제값과 예측값을 파악 가능하고, x,y축이 무엇을 의미하는 지 표시

**그래프에 대한 세부정보 출력**

데이터 포인터(원본데이터에서 리샘플링 된 데이터 개수) 파악하고, y축에 해당하는 측정된 값의 범위 파악 가능

**예측 결과 통계 출력**

1. Mean Actual Value와 Mean Predicted Value

목적 : 실제 값과 예측 값의 평균을 비교하여 모델이 실제 데이터를 얼마나 잘 추정하는 지 평가

분석 방법 :

- 두 개의 값이 비슷하면 모델이 데이터의 중심 경향을 잘 추정하고 있다는 의미
- 두 값이 크게 차이난다면 모델이 데이터의 평균 수준을 잘 예측하지 못한다는 의미

1. Variance of Actual Values와 Variance of Predicted Values

목적 : 실제 값과 예측 값의 분산(변동성)을 비교하여 모델이 데이터의 변동성을 얼마나 잘 반영하는지 평가

분석 방법 :

- 두 분산이 비슷하면 모델이 데이터의 변동성을 잘 반영하고 있다는 의미
- 예측 값의 분산이 실제 값의 분산보다 훨씬 작으면 모델이 데이터의 변동성을 충분히 반영하지 못한다는 의미
- 예측 값의 실제 값의 분산보다 크면 모델이 과적합되어 있음을 시사

1. RMSE(Root Mean Square Error)

목적 : 모델의 예측 값과 실제 값 간의 평균적인 차이를 나타내는 지표로, 모델의 전반적인 예측 정확도를 평가

분석 방법 :

- RMSE 값이 작을 수록 모델의 예측이 실제 값에 가까워짐을 의미
- RMSE 값이 크면 모델의 예측이 실제 값과 다르다는 의미
- 예를 들어, RMSE 값이 10이라면 모델의 예측이 실제 값과 평균적으로 10정도의 차이를 보인다는 것을 의미

**잔차 분석**

잔차는 실제 값과 예측 값의 차이를 나타낸다. 잔차가 작을수록 모델의 예측이 실제 값에 더 가깝다는 것을 의미한다. 

1. 편향(Bias) 확인

목적 : 잔차의 평균을 통해 모델의 예측 정확성 평가

분석 방법 :

- 잔차의 평균이 0에 가까울수록 모델의 예측이 편향되지 않았음을 의미
- 잔차의 평균이 0에서 크게 벗어난다면, 모델이 일관되게 실제 값보다 높거나 낮게 예측하고 있을 가능성 존재

1. 분산(Variance) 확인

목적 : 잔차의 분산을 통해 예측 값이 실제 값에서 얼마나 벗어나는지 파악

분석 방법 : 

- 낮은 분산은 모델이 안정적인 예측을 제공함을 의미
- 높은 분산은 모델이 데이터의 일부 패턴을 잘못 학습하거나 데이터 자체가 매우 변동적임을 시사

1. 이상치 식별

목적 : 잔차의 최대 / 최소값을 통해 모델의 예측 정확성 평가

분석 방법 : 

- 잔차의 최대 / 최소값이 모델에서 크게 벗어난 예측을 한 경우(이상치) 값을 파악

**이상치 확인**

목적 : 이상치 확인을 실제로 확인

분석 방법 : 

- 잔차의 절대값이 잔차 표준 편차의 2배를 초과하는 경우를 이상치로 간주, 이는 통계적으로 약 95%의 데이터가 평균 ±2표준편차 범위 내에 들어온다는 가정에 기초(정규 분포 특성에 기반)
- 위의 식을 통해 이상치의 개수를 출력하여 파악
- 이상치에 해당하는 데이터를 실제로 출력하여 파악

위의 코드를 수정한 후 실행한 결과는 다음과 같다.

- lstm_performance_graph.tiff

![week5_13](https://github.com/Kyeong6/whatever/assets/100195725/6517fe21-2809-4f31-a195-c88452f723f3)


- 2_Learning_LSTM.py

![week5_14](https://github.com/Kyeong6/whatever/assets/100195725/889ac4e2-558c-419a-bb76-7ea32d2069b9)


위 결과값을 간단하게 해석하자면, 전반적으로 데이터의 변동성을 반영하지 못한다는 문제점이 존재한다.
