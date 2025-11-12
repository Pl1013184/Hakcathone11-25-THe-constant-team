import lgpio
import time

CHIP = 0
SERVO_PIN = 18        # Use BCM 18 (physical pin 12). Works great for PWM.
PULSE_MIN = 500       # ~0°
PULSE_CENTER = 1500   # ~90°
PULSE_MAX = 2500      # ~180° (many servos are 2300-ish max)

h = lgpio.gpiochip_open(CHIP)
try:
    # Claim the pin as an output
    lgpio.gpio_claim_output(h, SERVO_PIN)

    # Center
    print(f"Center {PULSE_CENTER}us")
    lgpio.tx_servo(h, SERVO_PIN, PULSE_CENTER)  # 50 Hz is default
    time.sleep(2)

    # Min
    print(f"Min {PULSE_MIN}us")
    lgpio.tx_servo(h, SERVO_PIN, PULSE_MIN)
    time.sleep(2)

    # Max
    print(f"Max {PULSE_MAX}us")
    lgpio.tx_servo(h, SERVO_PIN, PULSE_MAX)
    time.sleep(2)

    # Back to center
    print(f"Center {PULSE_CENTER}us")
    lgpio.tx_servo(h, SERVO_PIN, PULSE_CENTER)
    time.sleep(2)

finally:
    # Stop pulses and clean up
    lgpio.tx_servo(h, SERVO_PIN, 0)  # 0 stops servo signal
    lgpio.gpio_free(h, SERVO_PIN)
    lgpio.gpiochip_close(h)
