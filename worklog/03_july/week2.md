# 업무내용

- 파이프라인 질문사항 작성

## 7/8

### 질문사항

1. 센서를 통해 얻는 데이터 간격을 어떻게 설정할 것인가?  
   
    - 10분이라고 했을 때 0~10분 데이터를 다 받는 것인지, 아니면 10분 값 하나 만 받는 것인지?
  
    - 결국 웹사이트에서 어떻게 표현할 것인지가 답이 될 것
  
    - 질문에 대한 답변을 통해 DB 선택 가능
  
2. 결과값 데이터 전송 간격도 센서를 통해 얻는 데이터 간격과 동일하게 하면 되는 것인지?
   
3. 현재 관리자가 특정 기간에 데이터를 확보한다고 했는데, 기기에서 사내 중앙 서버로 보내는 과정은 존재하니 중앙 서버에서 따로 DB를 구축해서 기기 별로 데이터 저장하는 것이 어떤지?
    - 관리자가 장치에 접근하여 데이터 확보하는 방법의 모호함에서 비롯된 의문
  
4. 이상치도 예측값으로 전달(알림)하는지? 
    - 실제 이상치일 때 전달인지, 예측값을 통해 얻은 이상치가 나올 경우를 전달하는지?
  
    - 실제 이상치 : 실시간성을 반영한 DB 사용 고려
  
    - 예측값 이상치 : 실시간성 반영 DB 사용 대신 일반적인 DB 사용 고려
<br/></br>

### 파이프라인 구성

![Untitled](https://github.com/Kyeong6/whatever/assets/100195725/a41ae72c-678a-46dd-8306-ebbbc0f00f57)
<br/></br>

**Our works**

| No. | Work | Description |
| --- | --- | --- |
| 1 | 데이터 확인 | Sensor를 통해 얻은 데이터 형식을 확인 |
| 2 | DB 선택 | Raw data를 저장할 데이터베이스 선택 |
| 3 | DB 테이블 구성 및 적재 | Raw data 테이블 구조에 맞게 적재 |
| 4 | DB 조회 후 형식 변환 | DB에 적재된 데이터를 LSTM 모델 예측을 수행할 수 있게 CSV 형식으로 변환 후 Input 디렉토리에 위치 |
| 5 | 데이터 형식 변환 | 예측 수행을 위한 데이터 형식 변환 [0] : 시간(datetime), [1] : 실제값(float) |
| 6 | 예측 수행 | 예측값 저장 : Output/Prediction/prediction.csv<br>이상치 : 10min<br>예측값 : 1hr |
| 7 | 예측값 전송 | CSV(prediction.csv) 파일 API로 전송<br>전송 방식 : requests 라이브러리 사용<br>(전송 방식은 Front 요청에 따라 JSON 형식으로 변환 후 전송할 수 있음) |
| 8 | 예측값 저장 | 예측값을 저장(아래 중 택 1), 설정한 주기가 되면 중앙 서버로 전송,<br>혹은 전송만 하고 중앙서버에 저장 및 처리하는 방식(기기 저장하는 이유 사라짐)<br>1. csv 파일을 특정 디렉토리에 저장<br>2. DB 예측값 컬럼에 값 저장(범위를 통해 조회한 후 전송 진행) |
| 9 | 스케줄러 도입 | 위 과정을 설정한 각 주기에 따라 백그라운드 실행 |
<br/></br>
## 7/9

### 질문에 대한 답변

1. 센서를 통해 얻는 데이터 간격을 어떻게 설정할 것인가?

→ 센서는 1분에 한 번씩 데이터 수집 후 DB에 전달

1. 결과값 데이터 전송 간격도 센서를 통해 얻는 데이터 간격과 동일하게 하면 되는 것인지?

→ 결과값 전송(중앙 서버)은 기능 별로 다르다. 예측값은 1일 1회, 이상치는 존재할 경우 전송

1. 현재 관리자가 특정 기간에 데이터를 확보한다고 했는데, 기기에서 사내 중앙 서버로 보내는 과정은 존재하니 중앙 서버에서 따로 DB를 구축해서 기기 별로 데이터 저장하는 것이 어떤지?

→ 백업 개념으로 1년치 데이터를 기기에서 저장

 

1. 이상치도 예측값으로 전달(알림)하는지? 

→ 이상치는 예측값을 사용하지 않고 1분 간격으로 데이터를 확인하여 이상치 있을 경우(조건) 전송
<br/></br>
### 프로젝트 개발 단계

**정책**

- 1일 1통신 진행
- 
- 향후 일주일의 예측값을 다음 날 특정 시간에 전송
    - Ex) 7월 1일 기준 7월2일부터 8일까지의 예측값 전송
    - 
- 기기에 1년간의 실제, 예측값을 저장하는데 예측값은 가장 예측 확률이 높은 값 저장
    - Ex) 7월 1일 데이터를 사용해서 7월 2~8일의 데이터를 예측하므로, 7월 2일에는 7월 3~9일을 예측한다. 결국 +7씩 다음 날로 이동하기 때문에 가장 예측 확률이 높은 경우는 바로 전날의 데이터를 가지고 예측을 진행한 예측값이다. 7월 1일 데이터를 사용했을 경우, 바로 다음 날인 7월 2일의 예측값을 저장하고, 7월 2일 데이터를 사용했을 경우, 마찬가지로 7월 3일의 예측값을 저장한다.
<br/></br>

**CSV 파일 구조(센서 데이터 저장**)

| time | value |
| --- | --- |
| 2024-07-09 0:00 | 224 |
| 2024-07-09 0:01 | 227 |
<br/></br>

**예측값 플로우**

| No. | Work | Description |
| --- | --- | --- |
| 1 | 목업 데이터 사용 | Sensor를 통해 얻은 데이터를 대신 csv 파일에 목업데이터를 설정해 개발 진행, 실제로는 센서의 분당 데이터 사용 |
| 2 | 데이터 조회 및 이동 | 시간 당 목업데이터를 조회하여 이전 시간의 60개의 행을 Input(LSTM 디렉토리 내에 존재하는 디렉토리)에 위치<br>Ex) 2시에 대한 예측값을 위해서는 0 ~ 1(60 rows)시의 데이터 필요 |
| 3 | 데이터 형식 변환 | csv 파일 데이터를 Prediction.py를 실행할 수 있게 데이터 형식 변환<br>timestamp : datetime<br>value : float |
| 4 | 예측 수행 | LSTM 모델을 통한 예측 수행 후 예측값 저장 : Output/Prediction/prediction.csv<br>예측 방법 : 1일 1분당 정책으로 인한 ID+반 복사 방식 (i = 1 ~ 6) |
| 5 | 예측값 저장 및 전송 | 1분 ~ 60분으로 총 6개의 파일의 24개의 행에 존재한다.<br>1일 1회 CSV(Day(step))prediction.csv 파일을 서버로 전송<br>전송 방식 : requests 라이브러리 사용<br>(전송 방식은 요청방식에 따라 JSON 형식으로 변환 후 전송할 수 있음)<br>전송한 후 파일은 리셋 진행함. |
| 6 | 스케줄러 도입 | 위 과정을 설정한 주기에 따라 백그라운드 실행 |

<br/></br>
**이상치 플로우**

| No. | Work | Description |
| --- | --- | --- |
| 1 | 목업 데이터 사용 | Sensor를 통해 얻은 데이터를 대신 csv 파일에 목업데이터를 설정해 개발 진행 |
| 2 | 참조 | 예측값은 조회한 후 csv 파일에 넣지만, 분당 데이터를 기반으로 이상치 파악을 하기 때문에 데이터를 바로 참조 진행 |
| 3 | 이상치 확인 | 이상치 파악 방법 : 정규분포 사용하여 단계(변수) 설정<br>0단계 : 정상<br>1단계 관심 : 90 ≤ value ≤ 95<br>2단계 주의 : 95 ≤ value < 98<br>3단계 경계 : 98 ≤ value < 99<br>4단계 심각 : 99 ≤ value ≤ 100 |
| 4 | 알림 | 이상치일 경우 JSON 파일 형식으로 전달<br>{<br>”machine_number” : 1<br>”time” : 2024-07-09 0:01,<br>”outlier_stage” : 3,<br>”value” : 227<br>}<br>(machine_number 같은 경우 중앙 서버에서 구별할 수 있으면 제거) |
| 5 | 스케줄러 도입 | 위 과정을 설정한 주기에 따라 백그라운드 실행 |

### Trouble Shooting

기존에 생각한 방식은 하루의 데이터를 1시간 단위로 나누어 예측을 진행하면 될 것이라고 생각하였으나, 해당 방식은 그저 하루의 예측값을 보내는 것과 다를 바 없다. 왜냐하면 1일 1통신을 진행하기 때문에 결국 일주일 예측값을 보내야 하기 때문이다. 

최종적인 구현을 예를 들면 다음과 같다.

7월 1일 데이터를 활용해서 7월 2~8일(총 7일) 데이터를 예측하는 데, 이때 각각 1일 24 rows를 가져야 한다.
(1시간마다 예측 진행)

이것을 구현하기 위해서는 7월 1일 기준으로 6월 30일 23시 ~ 7월 1일 00시 데이터를 참고해서 다음 날인 7월 2일의 0 ~ 1시 예측을 진행해야 한다. 즉, 결국 1D + 1H 예측을 진행해야 하는 것이다.

일주일 간의 예측 방법은 다음과 같이 2가지 방법이 존재한다.

1. 기존 실제 값을 사용하여 2D+1H , 3D+1H… 같이 진행
2. 1D+1H를 실제 값으로 간주하여 다음 날 예측 진행

직관적으로는 실제 값을 기반으로 예측하는 첫 번째 방식이 좋을 것이라고 생각하지만, 1, 2번 방식 모두 테스트하여 좋은 성능을 보이는 것을 채택 필요.

### 질문사항

1. 예측값, 이상치 데이터를 저장할 때 어떤 내용이 존재해야하는가?
2. 자체적으로 이상치 기준을 설정하는데 환경에 따라 바뀌는 데 이것 또한 정의가 되었을 것 같다. 어디에 맞춰서 진행을 하면 좋을지? 개발 단계에서는 구현만 진행해야하는 지?
<br/></br>
## 7/10

### LSTM 모델 코드 수정

LSTM 모델을 작동하는 연구실에서 실행 도중 발생한 에러와 질문 사항을 해결하는 업무 진행

**에러 사항**

1. 2_Learning_LSTM.py를 `-w 7 -p 1 -hp -e 700 -b 32 –l` 인자로 실행하면 학습이 끝나지 않은 오류
    - `-l` 는 설정한 기본값으로 실행하는 인자이기 때문에 제외하고 실행해야 함
    - `-l` 을 제외하고 실행하면 `AttributeError: module 'Training' has no attribute 'train_test_split’` 가 발생하는 데 코드를 수정하는 단계에서 validation 데이터셋도 추가해서 2_Learning_LSTM.py에서 다음과 같이 수정이 필요하다.
    
    ```python
    # 학습 데이터 / 테스트 데이터 분할
            train, val, test = training.train_val_test_split(df)
    ```
    
    - 다음과 같이 작성하면 그래프 또한 인자를 반영해서 생성된다.

**질문 사항**

1. 전처리 → 학습 → 예측까지 끝나고 예측된 시계열 데이터 저장까지 끝난 상황에서 lstm_performance_graph를 확인해보니 그래프 제목 부분에 기존에 설정했던 epoch 값인 700이 아닌 200으로 나왔습니다. 어떻게 해결할 수 있나요?
    - 해당 오류 또한 에러 사항과 동일한 문제이다.
2. 다른 수질 데이터를 구동하고자 할 때, 기존의 파일들 중 수정해야하는 부분이 있는지 궁금합니다.(분석 대상 데이터의 형식을 날짜와 값 형식으로 변환하기만 하면 되는지 궁금합니다.)
    - 3_Prediction.py를 이용해서 예측을 진행하는 데, 이때 `-f` 를 통해 ‘파일명’을 설정합니다. 파일의 데이터셋은 1행에 날짜, 2행에 값 구조로 설정 필요
    - Prediction.py에서 1행과 2행을 날짜, 값으로 인식하기 때문이다.
    
    | timestamp | value |
    | --- | --- |
    | 2024-07-09 0:00 | 4.21 |
3. 새로운 데이터(단위나 특성이 다른 경우) 인자에 할당되는 코드 수정이 필요한 것인지? 어느 부분을 수정하여 사용할 수 있는지?
    - 이 부분은 에러 사항과 동일합니다. 기본값을 실행했을 때 코드 수정했던 내용들이 반영되도록 작성하여서 인자를 바꿀 때 정상적으로 작동되게 구현을 해야해서 이용자 입장에서 수정이 필요하지는 않고, 제가 수정하도록 하겠습니다.
4. 개발된 LSTM 알고리즘에서 같은 RNN 계열인 GRU, 기본 RNN 알고리즘으로 코드를 수정하는 것은 가능할 것 같다고 판단하였는데, 오코캠코더(?), Transformer와 같이 RNN 계열이 아닌 다른 구조와 원리를 가지고 있는 알고리즘의 경우에는 기존 LSTM 파이프라인에서 어느 정도의 코드 수정을 통해 구현이 가능한지?
    - RNN 계열의 알고리즘으로의 코드 수정은 모델 정의 부분에서의 수정 필요합니다. 또한, 예측의 성능을 올리기 위해서는 좋은 예측값을 도출하는 하이퍼 파라미터의 값도 파악해야해서 같은 RNN 계열이라도 수정은 가능하지만 시간 소요가 꽤 걸릴 것입니다.
    - Transformer 모델은 Self-Attention 매커니즘을 기반으로 하고있는데, 이는 RNN과는 매우 다른 구조로 되어있어 시간 소요가 많을 것입니다. 즉, 모든 부분을 수정한다고 보시면 될 것 같습니다. 데이터 전처리 과정 또한 추가적으로 Transformer에 맞게 수정해야하기 때문입니다. 전반적인 변경사항은 다음과 같습니다.
        - 데이터 전처리
        - 모델 정의
        - Transformer와 데이터에 맞는 최적화 하이퍼 파라미터 튜닝
5. 설정한 LSTM 환경에서 학습을 시킬때 할때마다 30~40분 정도 소요되던데, 이때 학습 내용이 리셋되고 새로운 학습을 시키는 건가요?? 아니면 학습 내용이 계속 축적되는 건가요?
    - 새롭게 학습하면 기존 내용은 리셋되고 새로운 학습이 진행됩니다.
6. 예측 데이터에서 1월 8일부터 데이터 나오는 이유가 아래 설명이 맞나요?
Learning_LSTM.py의 43줄 training.training(7, 1)에서 7이 window_size라서 1월 8일 부터 예측됨 / 임의 조정하려면 2_Learning_LSTM.py의 arguments 인자를 사용자가 바꿔줘야함
    - 현재 기본값은 window_size가 7로 설정되어있습니다. window_size를 명령어를 실행할 때 인자를 통해서 변경할 수 있습니다. window_size란 간단하게 말하면 설정한 크기만큼 앞에 데이터(행)을 참고하는 것입니다. 그래서 현재 데이터셋이 1월1일부터 존재하면 7개를 참고해서 1월8일의 값부터 예측을 진행하는 것입니다.
7. 사용하려는 수량 및 수위 데이터가 중간중간에 날짜가 빠진게 있어서 임의로 빠진 날짜는 빈칸으로 채워서 전처리를 진행했는데, 혹시 전처리 과정에 빠진 날짜가 있으면 알아서 선형보간을 하는 방식인가요?
    - 해당 날짜의 값이 없는 결측치일 경우에는 데이터 전처리 과정에서 처리할 수 있습니다.(Data_preprocessing.py의 Missing 함수 : 최대 3개의 연속 결측값에 대해서는 정방향 채우기를 사용하고, 3개보다 긴 결측값 시퀀스에는 선형 보간을 사용합니다.)
    - 다만 언급해주신 날짜가 결측치인 경우에는 에러가 발생해서 추가적인 전처리 과정이 필요합니다.

### 질문사항에 대한 답변

1. 예측값, 이상치 데이터를 저장할 때 어떤 내용이 존재해야하는가?
    - 시간
    - 수압(실제값)
    - 수량(실제값)
    - 수압(예측값)
    - 수량(예측값)
    - 실제값은 센서를 통해 바로 저장되기 때문에, 예측값을 전송한 후 이를 저장하는 스크립트 구현 필요
2. 자체적으로 이상치 기준을 설정하는데 환경에 따라 바뀌는 데 이것 또한 정의가 되었을 것 같다. 어디에 맞춰서 진행을 하면 좋을지? 개발 단계에서는 구현만 진행해야하는 지?
    - 개발 단계에서는 정규분포를 사용하여 다음과 같이 단계를 나눈다.
    - 1단계 관심 : 90 ≤ value ≤ 95
    - 2단계 주의 : 95 ≤ value < 98
    - 3단계 경계 : 98 ≤ value < 99
    - 4단계 심각 : 99 ≤ value ≤ 100

### 추가적인 구현 사항

1. 가장 최신의 예측값, 즉 일주일 간의 예측을 하루씩 얻는데 이 중 당일의 예측값을 저장한다는 개념
    - 개념을 설명 하기 어려우니 도식화해서 표현

### 파이프라인 설계 시안 도식화

![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/0c79766f-e6e5-47fb-bb1f-6711656123dd/f7b9a22f-af45-4ecc-818c-c498649386a8/Untitled.png)

### CSV 도입이유

**장점**

1. 간단하고 빠른 설정:
    - 별도의 데이터베이스 설치나 설정이 필요 없으며, 데이터를 쉽게 저장하고 열 수 있다.

**성능 최적화 방법**

1. 부분 데이터 로드:
    - pandas 라이브러리나 CSV 모듈을 사용하여 필요한 부분만 효율적으로 읽을 수 있다. 예를 들어, 최신 60개 항목만 읽는 경우 전체 파일을 읽지 않아도 된다.(Sync 고려한 코드 작성 필요)
    
    ```python
    python코드 복사
    import pandas as pd
    
    # 필요한 열만 선택하여 읽기
    df = pd.read_csv('data.csv', usecols=['timestamp', 'value'])
    
    # 최신 60개 항목만 선택
    recent_data = df.tail(60)
    ```
    
2. 파일 크기 관리:
    - 데이터가 지속적으로 쌓일 경우 주기적으로 파일을 분할하거나 오래된 데이터를 아카이브하는 방식이 적용하기. 예를 들어, 한 달치 데이터를 하나의 파일로 저장하고, 매달 새로운 파일을 생성하는 방법
3. 동시 접근 제어:
    - 동시성 문제가 발생하지 않도록 파일 잠금 메커니즘을 사용하여 여러 프로세스가 동시에 CSV 파일에 접근하지 않도록 한다. 이상치 예측은 csv 파일에 접근하지 않기 때문에 도입이 가능하다.

### 결론

CSV 파일은 간단한 사용성을 제공하여, 최신 60개 항목만 조회하는 경우에는 성능 이슈가 크게 발생하지 않을 가능성이 높습니다. 그러나 데이터가 계속 쌓여 파일 크기가 커질 경우 파일 분할 및 관리 전략을 세우는 것이 중요하다. 제품 시안 단계인 초기에는 CSV 파일로 시작하고, 성능(시간, 메모리)을 확인한 후 이슈가 발생하거나 데이터베이스(SQLite3)와 비교하여 좋지 않은 성능을 보일 경우 데이터베이스로 전환하는 방식을 도입할 예정이다.