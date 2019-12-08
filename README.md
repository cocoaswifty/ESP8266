# ESP8266

ESP8266 NodeMCU Lua V3 ESP-12E with MicroPython

### 規格
- 串口芯片：CH340
- 源流最高值 12mA，潛流最高值 20mA。


### nodeMCU 驅動程式安裝

1. 板子 USB 連接電腦。
2. 安裝 [nodeMCU 非官方驅動程式](https://goo.gl/YAys6k)，直接用 Homebrew 安裝驅動程式 ，注意有些 USB 線會讀不到 Port。
3. `$ ls -l /dev/tty.\*`
4. 確認 Port 有 tty.wchusbserial1410

### MicroPython 安裝

5. 下載韌體 http://micropython.org/download#esp8266 選擇 Esptool 版本。
6. 安裝 Esptool \$pip install esptool
7. 先清除記憶體 `$ esptool.py --port /dev/tty.<port-name> erase_flash`
8. 開始燒錄韌體 `$ esptool.py --port /dev/tty.<port-name> --baud 115200 write_flash --flash_size=detect -fm dio 0 <firmware-file>.bin`
9. 連接控制板 `$ screen /dev/tty.<port-name> 115200`
10. Ctrl+A, K 可離開 screen

### REPL(Read Evaluate Print Loop) 模式

MicroPython 說明文件：
http://docs.micropython.org/en/latest/esp8266/quickref.html

試著點亮 Pin2 板子上預設的 Led。

    > from machine import Pin
    > led = Pin(2, Pin.OUT)
    > led.value(0) //輸出低電位，Pin2 是相反的
    > led.value(1) //輸出高電位

### Ampy 安裝

11. 安裝 ampy 用來上傳程式到板子 `$ sudo pip install adafruit-ampy`
12. 攥寫閃爍 LED 程式 `blink.py`
13. 直接執行程式 `ampy --port /dev/tty.<port-name> run blink.py` 若出現 Error http://bit.ly/33X3TuC
14. 上傳到板子 `ampy --port /dev/tty.<port-name> put blink.py`
15. 在 REPL(Read Evaluate Print Loop)模式 `$ screen /dev/tty.<port-name> 115200` 中執行 import blink
16. 列出所有檔案 `ampy --port /dev/tty.<port-name> ls`
17. 下載檔案 `ampy --port /dev/tty.<port-name> get blink.py ~/Downloads/blink.py`
18. 刪除檔案 `ampy --port /dev/tty.<port-name> rm blink.py`

## NodeMCU 開發板

- 輸入輸出電壓限制是 3.3 V，最大輸出電流是 12mA。
- 建議不要使用 GPIO6 ～ GPIO11，GPIO6 ～ GPIO11 被用於連接開發板的閃存(Flash Memory)。
- GPIO2 引腳 在 NodeMCU 開發板啟動時是不能連接低電平的。
- GPIO15 引腳在開發板運行中一直保持低電平狀態。因此請不要使用 GPIO15 引腳來讀取開關狀態或進行 I²C 通訊。
- GPIO0 引腳在開發板運行中需要一直保持高電平狀態。否則 ESP8266 將進入程序上傳工作模式也就無法正常工作了。NodeMCU 的內置電路可以確保 GPIO0 引腳在工作時連接高電平而在上傳程序時連接低電平。
- GPIO 0-15 引腳都配有內置上拉電阻。
- GPIO16 引腳配有內置下拉電阻。
- 選購上，可以優先考慮 V2 CP2102 的版本。

* https://pan.baidu.com/s/1dDkYKpV
* http://www.taichi-maker.com/homepage/esp8266-nodemcu-iot/iot-micropython/
* https://www.liaoxuefeng.com/wiki/1016959663602400/1017606916795776
* http://boywhy.blogspot.com/2018/09/esp8266-micropythonnode-mcu-os-x.html
* http://bit.ly/38jihRp
  
![NodeMCU 接口圖](http://www.ifuturetech.org/ifuture/uploads/2017/07/AMICA-NODEMCU-ESP8266-LUA-CP2102-WIFI-DEVELOPMENT-MODULE-IOT-gujarat.png)
