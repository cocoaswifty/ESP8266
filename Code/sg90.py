from servo import Servo
import time
import mini
import random


class Target(Servo):
    def rand(self):
        r = random.randint(0, 180)  # 0~180的隨機數
        print('Turn to ' + str(r))
        self.rotate(r)


s1 = Target(mini.D4)

s1.rotate(180)
time.sleep(5)
s1.rand()  # 隨機旋轉
time.sleep(5)
s1.rotate(0)
