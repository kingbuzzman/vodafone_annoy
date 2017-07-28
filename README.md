Mac OSX ONLY!!!!
```
while true; do
  # get my current wireless name
  wifi_name=$(/Sy*/L*/Priv*/Apple8*/V*/C*/R*/airport -I | grep SSID | grep -v BSSID | tr -d ' ' | cut -d ':' -f 2)
  # get my vodafone router ping average
  router_ping_avg=$(ping -c4 $(netstat -nr | grep '^default' | grep UGSc | tr -ds '\t' ' ' | cut -d ' ' -f 2) | tail -n 1 | cut -d '=' -f 2 | cut -d '/' -f 2)
  # save the speedtest data and append the wifi name and router ping
  speedtest-cli --csv | awk '{print $0",'$wifi_name','$router_ping_avg'"}' >> $(pwd)/vodafone.csv;

  gnuplot <(echo "
  set title 'Vodafone Es Conexión'
  set ylabel 'Velocidad'
  set xlabel 'Hora'
  set grid
  set term png
  set xdata time
  set format x '%H:%M'
  set timefmt '%Y-%m-%dT%H:%M:%SZ'
  set datafile separator ','
  set output '$(pwd)/graph.png'
  plot '$(pwd)/vodafone.csv' using 4:6 title 'Ping (ms)' with lines linetype rgb '#808080',\
       '$(pwd)/vodafone.csv' using 4:10 title 'Router ping (ms)' with lines linetype rgb '#C0C0C0',\
       '$(pwd)/vodafone.csv' using 4:(\$7/1000000) title 'Download (Mbit/s)' with lines linetype rgb 'blue',\
       '$(pwd)/vodafone.csv' using 4:(\$8/1000000) title 'Upload (Mbit/s)' with lines linetype rgb 'red'
  ");

  git -c $(pwd) add $(pwd)/vodafone.csv
  git -c $(pwd) add $(pwd)/graph.png
  git -c $(pwd) commit -m "New data $(date '+%Y-%m-%d %H:%M:%S')"
  git -c $(pwd) push

  sleep 300;
done
```
