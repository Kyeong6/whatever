# 업무내용

- 코드 수정사항 반영

## 9/9

### 코드 수정사항 반영

1. ModuleNotFoundError: No module named 'apscheduler' > pip install apschedule
2. ModuleNotFoundError: No module named 'dotenv' > pip install python-dotenv
3. ModuleNotFoundError: No module named 'serial' > pip install serial > src/serial.py 와 pyserial 라이브러리 불러올때 사용하는 serial 명칭이 동일해서 문제생김
    - scheduling.py파일 내에 작성되어있는 10~15 코드 전부 from [스크립트명] → from src.[스크립트명]으로 변경
4. 현재 미완성상태라, outlier_detection.py 스크립트에서 OutlierDataSaver,AnomalyDetectionExecutor부분이 주석처리되어있음 > 임시로 주석해제함
5. concurrency.py 스크립트 2번 코드 from lstm_processor > from src.lstm_processor로 변경
6. core/config.py 스크립트 25번 초기기준경로설정 오타 수정 os.getenv("INITIAL_CRITERIA_DAT_PATH") >
os.getenv("INITIAL_CRITERIA_DATA_PATH")
7.  『WVR\src\build_criteria.py", line 147, in load_criteria_from_txt
criteria['mean_value'] = float(values[0])
ValueError: could not convert string to float: 'mean_value:'』
    - 현재 문제점 : flow_rate_crriteria.txt 파일에서 읽어들인 값을 float로 변경하지 못하고 있음.
    build_criteria.py 스크립트 line 141~154 확인해보니 공백을 기준으로 나눠 첫번째 요소인 `key:` 를 float로 변경시도하기 때문에 오류 발생
    - 해결방안 : 각 줄을 ": "(콜론과 공백) 기준으로 나누어 값을 추출하고 우측의 value값을 float로 변경시도하도록 수정

```python
# 수정 코드

with open(file_path, 'r') as file:
	for line in file:
	key, value = line.strip().split(": ", 1) # ': ' 기준으로 나누고, 첫 번째 ': '만을 기준으로 삼음
	
	# 각 키에 따른 값 변환 처리
	if key == 'mean_value':
	
		criteria['mean_value'] = float(value)
	elif key == 'std_dev':
	
		criteria['std_value'] = float(value)
	elif key == 'percentiles':
	
		criteria['percentiles'] = np.array([float(x) for x in value[1:-1].split(',')])
	elif key == 'upper_bound':
	
		criteria['upper_bound'] = float(value) if value != 'None' else None
	elif key == 'upper_multiplier':
	
		criteria['upper_multiplier'] = float(value) if value != 'None' else None
	elif key == 'lowest_avg_time':
	
		criteria['lowest_avg_time'] = value
	elif key == 'lowest_avg_value':
	
		criteria['lowest_avg_value'] = float(value) if value != 'None' else None
	elif key == 'night_flow_warning_levels':
	
		criteria['night_flow_warning_levels'] = [int(x) for x in value[1:-1].split(',')]
		
return criteria
```

8. apscheduler의 interval 매개변수는 days만 제공하고 months, years 제공하지 않아서 days로 months, years 값 수정 진행
9. scheduling.py의 SchedulerManager 클래스 내부메서드인 init에 데이터베이스 생성 함수를 먼저 설정(파이프라인 흐름상 데이터베이스 테이블 생성이 먼저 진행되어야 한다.)


## 9/10

### 테스트 코드 작성

- 현재 시리얼 통신을 이용한 테스트를 진행하지 못하므로 `from_sensor_data.txt` 를 1분에 한 번씩 읽어, 해당 데이터를 가지고 이상치 검출 / LSTM 예측을 수행하는 테스트 코드 작성

- 테스트 코드를 작성하고 난 후 실행 결과 현재 `ModuleNotFoundError: No module named 'core'` 에러가 발생
- 해당 문제는 프로젝트 운영체제가 Windows이므로, 시스템 변수로 `PYTHONPATH` 를 프로젝트 경로로 설정하여 terminal이 닫혀도 영구적으로 사용가능하도록 설정

- 테스트 진행을 하다보니 어디 부분이 오류가 난지 파악이 어려워 예외처리를 진행한 후 테스트 진행하여 오류를 잡는 방식으로 진행