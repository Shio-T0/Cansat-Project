
uv run InfoDisplay_Dashboard/main.py &
sleep(2)
zen-browser "localhost:4000" &
arduino-cli monitor -p "/dev/ACM0" -c baudrate=115200 > sensor_data.csv



