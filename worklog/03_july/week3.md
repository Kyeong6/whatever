# 업무내용

- 파이프라인 개발 진행

## 7/15

### 파이프라인 개발 일정

현재 이상치 기능에 대한 정의가 설정되어있지않아 **예측값 기능**을 먼저 개발한 후 이상치 기능을 개발할 예정이다.

### 파이프라인 아키텍처

**CSV**

![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/0c79766f-e6e5-47fb-bb1f-6711656123dd/97dd4ed3-dbbb-4b9d-9cd8-7d821ffc2202/Untitled.png)

**SQLite**

![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/0c79766f-e6e5-47fb-bb1f-6711656123dd/57431a96-1ce3-40e4-b78f-c4be27f6265d/Untitled.png)

CSV와 SQLite 방식을 도입하여 성능 평가를 진행할 예정이다.

### 성능 평가 요소

1. 쓰기 시간(Write)
2. 읽기 시간(Read)
3. 메모리 사용량(MEM)

테스트 과정을 반복수행하여 평균 성능을 측정할 예정이다.

### LSTM 관련 코드 설명

예측 정확성을 파악하기 위해 LSTM 모델을 수정을 했다. 파이프라인을 구현하기 위해서는 수정을 하지 않은 기존 코드를 이용해서 예측을 진행하는 것이 옳다고 판단하여 기존 코드에서 기능 구현을 하겠다.

**데이터 전처리 과정**

센서를 통해 분당 데이터를 적재하고 이후 60+window_size개의 행을 조회하여 LSTM 모델 예측을 진행해야 한다.(window_size는 예측을 진행하기 앞서 참고가 되는 데이터이므로 ) 그러므로 다음과 같은 수정사항이 존재한다.  
1. Data_Preprocessing.py의 TimeIntervalData 함수(시간 간격 병합)는 현재 1시간, 1일 기준으로 Input 데이터를 병합(resampling 과정)한다. 본 프로젝트에서는 분당 데이터를 병합을 하지 않아도 되기 때문에 time_interval 변수에 {’minutely’ : ‘1T’}를 추가한다. 또한 이를 기본값으로 설정한다.(명령어에서 기본 인자 사용)
<br/></br>

**예측 진행**

모델 학습같은 경우 기존에 학습된 모델을 사용하여 예측을 진행하기 때문에 해당 부분이 중요하다.