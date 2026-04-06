echo hello
sleep(3)
sleep 3
exit
ls
cd cansat/
ls
nvim main.py
cat main.py
exit
sudo touch /etc/systemd/system/cansat.service
ls
pwd
exit
sudo apt-get pynmea2
pip install mpu6050-raspberrypi pynmea2 pyserial adafruit-blinka adafruit-circuitpython-bmp3xx RPi.GPIO --break-system-packages
exit
pip install rpimotorlib --break-system-packages
exit
pip install mpu6050-raspberrypi --break-system-packages
python ./cansat.py 
sudo raspi-config
exit
python ./cansat.py 
exit
