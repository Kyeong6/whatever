# 업무내용

- 논의사항 정리
- 데이터셋 분리 확인 : 기존 방식인 개수 파악이 아닌 파일을 생성하여 실제로 분할 데이터셋 확인
- EDA 추가 : 분석에 필요한 추가적인 시각화 진행
- 프로젝트 아키텍처 설정 및 체크리스트 작성
    - ETL 작업
    - model 실행
    - 결과값 전송
- LSTM 알고리즘 Scale 조정 : 0 ~ 1000(그래프로 이해하기 쉽게)

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
