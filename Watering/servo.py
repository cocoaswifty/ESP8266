from machine import PWM, Pin


class Servo:
    total = 0

    def __init__(self, pin, min=500, max=2400, range=180):  # range 轉動角度範圍
        self.servo = PWM(Pin(pin), freq=50)
        self.period = 20000
        self.minDuty = self.__duty(min)
        self.maxDuty = self.__duty(max)
        self.unit = (self.maxDuty - self.minDuty)/range  # 每度的工作週期
        # Servo.total += 1
        # print('伺服馬達物件總數：' + str(Servo.total))

    def __duty(self, value):
        return int(value/self.period * 1024)    # 計算工作週期並取整數

    def rotate(self, degree=90):
        val = round(self.unit * degree) + self.minDuty  # 指定的工作週期，四捨五入
        val = max(self.minDuty, val)  # 比較最小週期跟工作週期，取大的
        val = min(self.maxDuty, val)  # 比較最大週期跟工作週期，取小的
        self.servo.duty(val)  # 選轉馬達
        # print('接在{}腳的馬達轉動到{}度。'.format(self.pin, degree))

    # def __del__(self):
    #     Servo.total -= 1
    #     print('刪除{}腳，剩餘{}個物件。'.format(self.pin, Servo.total))
