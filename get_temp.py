import RPi.GPIO as GPIO
import sys 
from re import findall 
from time import sleep 
from subprocess import check_output 

def get_temp():    
	temp = check_output(["vcgencmd","measure_temp"]).decode()        
	temp = float(findall('\d+\.\d+', temp)[0])                       
	return(temp)


while True:
	print("Temperatura: "+str(get_temp()))
	sleep(1)
