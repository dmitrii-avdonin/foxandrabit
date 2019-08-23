ECHO OFF
CLS
set PYTHONHASHSEED=0
set steps=1500
set width=150
set height=150
IF NOT [%1]==[] set steps=%1
IF NOT [%2]==[] set width=%2
IF NOT [%3]==[] set height=%3

FOR /l %%i in (1,1,21) DO (
	echo Reinforcement iteration %%i Start
	python ./src/main.py reinforcement %steps% %width% %height%
	echo Reinforcement iteration %%i End
)  

