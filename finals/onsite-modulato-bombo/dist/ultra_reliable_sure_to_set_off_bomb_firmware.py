import board
import pwmio
import time

# Choose a pin that supports PWM
pin = board.GP25


# Create PWM at 8 MHz with 50% duty cycle
pwm = pwmio.PWMOut(
    pin,
    frequency=7_080_000,
    duty_cycle=32768  # 50% of 65535
)

pwm2 = pwmio.PWMOut(
    board.GP23,
    frequency=7_130_000,
    duty_cycle=32768  # 50% of 65535
)

def p1on(): pwm.duty_cycle = 32768
def p1off(): pwm.duty_cycle = 0

def p2on(): pwm2.duty_cycle = 32768
def p2off(): pwm2.duty_cycle = 0

### Helper Functions ########

DELAY = 0.5

def pulse():
    p1on()
    time.sleep(DELAY)
    p1off()
    time.sleep(DELAY)

def send_sync():
    for _ in range(10):
        pulse()

def send_bit(bit):
    if bit == 1:
        p1on()
        time.sleep(DELAY)
        p1off()
        time.sleep(DELAY)
    else:
        # 0 = no pulse (or shorter pulse, depending on your protocol)
        time.sleep(DELAY*2)
        
def send_nbit_number(n, value):
    for i in range(4, -1, -1):  # MSB → LSB
        bit = (value >> i) & 1
        send_bit(bit)
        
def send_packet(numbers):
    # numbers = list of 4 integers (0–31)
    send_sync()
    for num in numbers:
        send_nbit_number(5, num)
    send_sync()
    

### Transmission
data = [1, 2, 3, 4]  # dummy pin
while True:
    time.sleep(10)
    send_packet(data)
