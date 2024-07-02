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

### Flow

![etl](https://github.com/Kyeong6/whatever/assets/100195725/f642452b-c30a-4023-bc8d-9231ab409398)

1. serial 통신과 Python script로 ETL 과정을 수행
2. 프로젝트 목적상 **실시간성**을 반영해야하므로 시계열 데이터 저장소로 많이 쓰이는 InfluxDB 사용(추후 변경사항)
3. Grafana를 통한 모니터링 시스템 구축(alert 기능 추가 필요)

**Reference**

- Grafana 이용한 대시보드 구축 : [Grafana로 실내/외 공기질 대시보드 구축하기 | 청정수의 Tech blog](https://blog.chungjungsoo.dev/dev-posts/airgradient-grafana-integration/)
