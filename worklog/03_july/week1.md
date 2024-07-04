# 업무내용

- 자문 미팅 관련하여 질문사항

## 7/1

### 질문사항

1. ETL 과정, Model pipeline 및 결과값 도출까지는 구현을 할 수 있으나 초기 단계인 raw data를 어떻게 받을 수 있나?
    - ~~찾아보니 RS485을 이용한 **시리얼 통신**으로 데이터를 받는 것 같다. (Window에 usb port 이용)~~
    - 자료조사를 통해 확인한 내용이 맞는지 자문받기
2. 결과값을 얻고난 후 최종적으로 전달을 해야하는 데 전달 방식은 어떻게 하면 되는지?

## 7/2

### 질문사항 답변

- 통신 부분 : 제조하는 업체가 존재
    - 제작업체에 따라 달라짐 → 제작업체에 요청
    - 장비를 먼저 확보하고 제작업체 요구하기
- 데이터 받는 것은 요청을 하면 되기 때문에 이후 과정(ETL)에 초점을 두자
- 데이터베이스 선정 : 조회 퍼포먼스를 고려해야하기 때문에 레코드 수 조절 필요
    - 파일 내부양을 작게하기

### 자료조사

**RS485을 이용한 시리얼 통신**

1. RS485 변환기(RS485를 USB나 RS232로 변환하는 장치), RS485 케이블 필요
2. 드라이버 설치 : 변환기를 USB에 연결하면 자동으로 드라이버 설치 가능
3. 포트 확인 : 변환기를 컴퓨터에 연결한 후, Windows의 장치 관리자에서 COM 포트 번호를 확인 
4. Python : `pip install pyserial` 
5. `pyserial` 라이브러리를 이용해서 데이터 받기

**데이터베이스 저장 예시**

```python
import serial
import sqlite3
import time

# 시리얼 포트 설정
ser = serial.Serial(
    port='COM3',  # 장치 관리자에서 확인한 COM 포트 번호
    baudrate=9600,  # 데이터 전송 속도 
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)

# 데이터베이스 연결
conn = sqlite3.connect('example.db')
cursor = conn.cursor()

# 테이블이 없을 경우 테이블 생성 
cursor.execute('''CREATE TABLE IF NOT EXISTS data (timestamp TEXT, value TEXT)''')

# 데이터 삽입 함수
def insert_data(timestamp, value):
    cursor.execute("INSERT INTO data (timestamp, value) VALUES (?, ?)", 
    (timestamp, value))
    conn.commit()

# 시리얼 통신으로 데이터 수신 및 데이터베이스에 저장
try:
    while True:
		    # 수신된 데이터가 있는지 확인
        if ser.in_waiting > 0:  
		        # 데이터를 읽고 디코딩
            data = ser.readline().decode('utf-8').rstrip() 
            print(f"Received data: {data}")
            insert_data(time.strftime('%Y-%m-%d %H:%M:%S'), data)
except KeyboardInterrupt:
    print("Communication stopped.")
finally:
    ser.close()
    conn.close()
```

**csv 파일 저장 예시**

```python
import serial
import csv
import time
import os
from datetime import datetime, timedelta

# 시리얼 포트 설정
ser = serial.Serial(
    port='COM3',  # 장치 관리자에서 확인한 COM 포트 번호
    baudrate=9600,  # 데이터 전송 속도 
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)

# CSV 파일을 저장할 디렉토리
csv_dir = 'csv_data'
if not os.path.exists(csv_dir):
    os.makedirs(csv_dir)

# 현재 시간으로 CSV 파일 이름 설정
current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
csv_file = os.path.join(csv_dir, f'data_{current_time}.csv')

# CSV 파일이 없으면 헤더 작성
if not os.path.exists(csv_file):
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['timestamp', 'value'])

# 데이터 CSV 파일에 삽입 함수
def insert_data(timestamp, value):
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, value])

# 오래된 파일 삭제 함수
def delete_old_files(directory, days=3):
    now = datetime.now()
    cutoff = now - timedelta(days=days)
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            file_time = datetime.fromtimestamp(os.path.getctime(file_path))
            if file_time < cutoff:
                print(f"Deleting old file: {filename}")
                os.remove(file_path)

# 시리얼 통신으로 데이터 수신 및 CSV 파일에 저장
try:
    while True:
		    # 수신된 데이터가 있는지 확인
        if ser.in_waiting > 0:  
		        # 데이터를 읽고 디코딩
            data = ser.readline().decode('utf-8').rstrip()  
            print(f"Received data: {data}")
            insert_data(time.strftime('%Y-%m-%d %H:%M:%S'), data)
        # 오래된 파일 삭제
        delete_old_files(csv_dir)  
except KeyboardInterrupt:
    print("Communication stopped.")
finally:
    ser.close()
```

### Flow example

![etl](https://github.com/Kyeong6/whatever/assets/100195725/f642452b-c30a-4023-bc8d-9231ab409398)

1. serial 통신과 Python script로 ETL 과정을 수행
2. 프로젝트 목적상 **실시간성**을 반영해야하므로 시계열 데이터 저장소로 많이 쓰이는 InfluxDB 사용(추후 변경사항)
3. Grafana를 통한 모니터링 시스템 구축(alert 기능 추가 필요)

**Reference**

- Grafana 이용한 대시보드 구축 : [Grafana로 실내/외 공기질 대시보드 구축하기 | 청정수의 Tech blog](https://blog.chungjungsoo.dev/dev-posts/airgradient-grafana-integration/)
<br/></br>
## 7/3

### ETL pipeline

![image](https://github.com/Kyeong6/whatever/assets/100195725/980163ad-2682-4c03-9c0f-de0075ec6099)

자문을 받은 뒤 **데이터 수신 구성**에 신경을 쓰는 것이 아닌 통신 이후 과정인 **데이터 처리 구성**에 초점을 두어야함을 인지

![image](https://github.com/Kyeong6/whatever/assets/100195725/1d8d60ba-a095-4e23-9060-d781454afb4a)


**Extract:** 데이터 수집 단계에서 수신한 데이터를 저장완료한 후 데이터 처리 단계에서의 **데이터 조회**에 해당

**Transform:** LSTM 모델이 예측하기 위한 형태로 변형

**Load:** 해당 프로젝트에서는 모델의 결과값을 저장이 아닌 전송의 의미
<br/></br>
### 프로젝트의 목적

1. 예측값 확인
    - 주기(1시간)를 설정하면 관리자가 예측값을 보고 이후 행동을 진행할 수 있다
2. 이상치 확인
    - 예측값보다 확인하는 주기를 빠르게 설정해서 조기검출 진행
<br/></br>

**목적에 따른 방향성 설정**

현재 LSTM pipeline 코드 상에서 Input 디렉토리에 csv파일을 넣어줘서 예측을 진행하고 있다. 

해당 과정을 데이터베이스를 구축한 후 조회(Extract)하는 방향으로 설정

- 어떤 데이터베이스를 사용할 것 인가?
    - Sqlite : IoT, 임베디드 장치에 적합한 데이터베이스, server-less
    - InfluxDB : 시계열 데이터에 특화된 데이터베이스(경량화되어있어서 임베디드 장치에도 사용 가능), not sever-less, NoSQL(조회속도 빠름) 구조
<br/></br>

**InfluxDB 특징**

1. 시계열 데이터에 최적화 : 저장 및 조회
    - 데이터는 시간 순서대로 저장
    - 시간 범위를 기준으로 데이터를 조회하는 등의 작업이 매우 빠르고 효율적
2. 높은 쓰기 및 쿼리 성능
    - InfluxDB는 초당 수십만 개의 데이터 포인트를 쓸 수 있으며, 대량의 데이터에 대한 쿼리도 빠르게 처리
    - 서버 모니터링, IoT, 실시간 분석 등의 분야에서 꼭 필요한 특징
3. 데이터 다운샘플링 및 보존 정책
    - InfluxDB는 자동으로 오래된 데이터를 다운샘플링하거나 삭제하는 기능을 제공
    - 저장 공간을 효율적으로 관리 가능
4. SQL-Like 쿼리 언어
    - InfluxDB는 InfluxQL이라는 SQL과 유사한 쿼리 언어를 제공
    - 익숙한 SQL 스타일의 문법으로 쿼리를 작성 가능
5. 확장성
    - InfluxDB는 클러스터링을 통해 데이터를 여러 노드에 분산시킬 수 있음
    - 데이터의 양이 늘어나도 성능을 유지하거나 향상 가능
6. 플러그인 시스템
    - InfluxDB는 Telegraf라는 플러그인 시스템을 제공
    - 다양한 소스에서 데이터를 수집하고, 다양한 출력 소스로 데이터를 전송 가능

데이터베이스에 적재한 데이터를 조회한 후 모델이 예측할 수 있게 Transform 과정을 수행해야 한다.   
현재 모델은 위에서 언급했듯이 Input 디렉토리에 존재하는 csv 파일을 통해서 예측을 수행한다. 
<br/></br>
**Transform 및 Prediction 과정**

1. 데이터베이스 조회
2. csv 변환 후 Input 디렉토리에 위치
3. LSTM 모델 예측 수행
4. Prediction.csv에 저장되는 결과값 전송