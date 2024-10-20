# 업무내용

- 피에스글로벌 요청사항
    - 미니PC pin번호 제거
    - 미니PC(서버) 실행 시 자동으로 기능 수행(python script 실행)

## 10/21

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

1. cnt가 10이 되지 못하고, current_minute가 “1, 11, 21, 31, 41, 51”이 되면(분단위 정각) cnt는 0으로 초기화 진행
2. cnt가 10이 되고, current_minnute가 “1, 11, 21, 31, 41, 51”이 될 경우 서버용 데이터 전송 수행