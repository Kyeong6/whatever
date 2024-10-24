# 업무내용

- 피에스글로벌 요청사항
    - 미니PC pin번호 제거
    - 미니PC(서버) 실행 시 자동으로 기능 수행(python script 실행)

## 10/21~25

### 피에스글로벌 요청사항

- Window pin(비밀번호 제거)
- window에서 .bashrc 파일 같은 것을 찾아서 실행되었을 때 자동으로 python script 실행할 수 있도록 구축
    - 배치 파일 작성(.bat)
        - 디렉토리 이동 명령어
        - 해당 스크립트 실행 명령어
    - 배치 파일 저장
    - 시작프로그램(window + r → shell:startup)에 배치 파일 위치

### 미니PC(서버) 실행 시 자동으로 기능 수행(python script 실행)

1. server.bat 파일 내용입니다.(파일 제공)

```bash
@echo off
REM Python 경로 환경변수 설정
echo Setting PYTHONPATH
set PYTHONPATH=%PYTHONPATH%;C:\Users\user\Desktop\WVR

REM 프로젝트 경로로 이동
echo Changing directory to project folder
cd C:\Users\USER\Desktop

REM Conda 가상환경 활성화
echo Activating Conda environment lstm_env
call conda activate lstm_env

REM main.py 실행
echo Running main.py
python main.py
```

1. server.bat 파일을 시작프로그램 디렉토리에 위치

위의 파일을 “시작프로그램” 디렉토리에 위치시키기위해서는 다음과 같은 과정이 필요합니다. 

- window키 + R을 통해 shell:startup 검색

![image](https://github.com/user-attachments/assets/10c7a302-996e-48a7-b650-b525a29f0f25)

- 시작프로그램 디렉토리에 server.bat 파일을 위치

![imag2e](https://github.com/user-attachments/assets/c89ee84c-42a3-4e4b-89bc-2c43df4c7747)

다음과 같은 과정으로 미니 PC 구동 시 자동으로 기능이 수행됩니다.

### 에러사항 해결

현재 서버 실행 기준으로 서버용 데이터를 전송하다보니 10시7분에 서버를 실행한다면 10시 17분에 서버용 데이터를 전송하는 경우가 발생한다. 현재 원하는 바는 10시 7분이 되더라도 11분 혹은 21분과 같이 정각+1분(예측값이 존재해야하기 때문)에 서버용 데이터를 전송해야하는 로직이므로 조건문 수정이 필요하다.

현재의 조건문은 다음과 같다.

- cnt가 10이 될 경우 서버용 데이터 전송 수행 → cnt는 센서 데이터 수집 1번이 곧, cnt = 1
    - 서버를 처음 실행할 경우 cnt는 0으로 초기화 되어있다.

**변경된 조건**

1. current_minute가 정각(0분, 10분 …) 및 cnt가 10이 될 경우 current_minnute가 “1, 11, 21, 31, 41, 51”와 같이 “정각+1분”에 서버용 데이터 전송 수행, 이후 cnt는 초기화 진행
2. current_minute가 정각이 되었지만, cnt가 10이 되지 못할 경우(즉, 서버 실행 직후 서버 데이터는 전송하지 않으려는 의도) “정각+1분”에 서버용 데이터 전송 수행하지 않음, 이후  cnt는 초기화 진행

**결론**

- 서버가 실행된 직후에는 데이터를 전송하지 않고, 정확히 `분+1`에 도달했을 때, 그리고 데이터 수집 횟수가 10번을 채웠을 때만 데이터를 전송 진행

**도식화**

![서버실행-도식화](https://github.com/user-attachments/assets/00a8db2d-b7e2-4926-91f4-922bbfbe0f53)

- 현재 코드

```python
# 데이터 수집 횟수 추적 카운터(__init__에 정의)
self.data_count = 0

# 수신받은 데이터 시간 확인하여 '분' 값 추출
timestamp = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')
current_minute = timestamp.minute

# 정각 + 1인 경우에 예측값 DB 조회
if current_minute == 1:
    # 예측 데이터 조회
    flow_preds, pressure_preds = self.get_all_predictions()
    
# 정각 + 1이 아닌 경우 예측 관련 값 0으로 설정
else:
    flow_preds = ["N"] * 7
    pressure_preds = ["N"] * 7  
    
# 데이터 카운터 증가 및 확인
self.data_count += 1
if self.data_count >= 10:
    # 10회 데이터 수집 후 tenmin 파일에 기록 (예측값 포함)
    self.ten_minute_transmitter.append_to_server_data(
        sensor_id, datetime_str, flow_rate, pressure,
        *flow_outlier_data, *pressure_outlier_data,
        flow_preds=flow_preds, pressure_preds=pressure_preds
    )
    self.data_count = 0
```

기존 코드를 서버 실행 후 예측 기능 수행 로직(알고리즘)에 맞게 변경한 결과는 다음과 같다.

- 변경 코드

```python
# 데이터 수집 횟수 추적 카운터(__init__에 정의)
self.data_count = 0

# 수신받은 데이터 시간 확인하여 '분' 값 추출
timestamp = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')
current_minute = timestamp.minute

# '정각(분)+1'일 때만 예측 데이터를 조회
if current_minute in {1, 11, 21, 31, 41, 51}:
    # 예측값 조회
    flow_preds, pressure_preds = self.get_all_predictions()
else:
    # 예측 데이터가 필요한 시간이 아니면, 기본값으로 설정
    flow_preds = ["N"] * 7
    pressure_preds = ["N"] * 7

# 데이터 수집 횟수를 증가, 수집 횟수 10번인지 확인
self.data_count += 1

# '정각(분)+1' 조건과 데이터 수집 횟수 조건을 모두 만족할 때만 서버용 데이터 전송
if current_minute in {1, 11, 21, 31, 41, 51} and self.data_count >= 10:
    # 서버 데이터 전송 로직
    self.ten_minute_transmitter.append_to_server_data(
        sensor_id, datetime_str, flow_rate, pressure,
        *flow_outlier_data, *pressure_outlier_data,
        flow_preds=flow_preds, pressure_preds=pressure_preds
    )
    # 전송 후 카운터 초기화
    self.data_count = 0  
    
# 아직 데이터 수집 횟수가 부족하거나, '정각(분)+1'이 아닐 경우
else:
		# 데이터 전송 없이 카운터만 초기화 진행(시간은 맞을 경우)
    if current_minute in {1, 11, 21, 31, 41, 51}:
        self.data_count = 0  

```