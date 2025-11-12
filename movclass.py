#!/usr/bin/env python3
"""
Servo Controller for Raspberry Pi using lgpio
Modern GPIO library recommended by Ubuntu
"""

import time
import sys

try:
    import lgpio
    print("lgpio library loaded successfully")
except ImportError as e:
    print("ERROR: lgpio library not available!")
    print("Install it with: sudo apt-get install -y python3-lgpio")
    print("Or: pip install lgpio")
    raise


class ServoController:
    """Controls a servo motor via PWM using lgpio"""

    def __init__(self, pin=18, min_angle=0, max_angle=180,
                 min_pulse_width=500, max_pulse_width=2500,
                 frequency=50, debug=True):
        """
        Initialize servo controller using lgpio

        Args:
            pin: GPIO pin number (BCM numbering, e.g., 18 for physical pin 12)
            min_angle: Minimum servo angle in degrees
            max_angle: Maximum servo angle in degrees
            min_pulse_width: Minimum pulse width in microseconds (default 500us)
            max_pulse_width: Maximum pulse width in microseconds (default 2500us)
            frequency: PWM frequency in Hz (typically 50Hz for servos)
            debug: Enable debug output
        """
        self.pin = pin
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.frequency = frequency
        self.current_angle = 90
        self.debug = debug

        # Servo pulse width parameters (in microseconds)
        self.min_pulse_width = min_pulse_width
        self.max_pulse_width = max_pulse_width

        # Initialize lgpio
        try:
            # Open GPIO chip (0 for Raspberry Pi)
            self.chip = lgpio.gpiochip_open(0)
            print(f"Opened GPIO chip: {self.chip}")

            # Claim pin as output
            lgpio.gpio_claim_output(self.chip, self.pin)
            print(f"Claimed GPIO pin {self.pin} (BCM numbering)")
        except Exception as e:
            print(f"ERROR initializing lgpio: {e}")
            raise

        # Start at center position
        self.set_angle(90, hold_time=0.1)

        print(f"\nServo controller initialized successfully!")
        print(f"Pin: {self.pin} (BCM numbering - physical pin 12)")
        print(f"Angle range: {self.min_angle}° to {self.max_angle}°")
        print(f"PWM frequency: {self.frequency}Hz")
        print(f"Pulse width range: {self.min_pulse_width}us to {self.max_pulse_width}us")
        print("Running on ACTUAL HARDWARE with lgpio")

    def _angle_to_duty_cycle(self, angle):
        """
        Convert angle to PWM duty cycle percentage

        Args:
            angle: Desired angle in degrees

        Returns:
            Duty cycle percentage (0-100)
        """
        # Clamp angle to valid range
        angle = max(self.min_angle, min(self.max_angle, angle))

        # Calculate pulse width for this angle
        angle_range = self.max_angle - self.min_angle
        pulse_range = self.max_pulse_width - self.min_pulse_width
        pulse_width = self.min_pulse_width + (angle - self.min_angle) * (pulse_range / angle_range)

        # Convert pulse width to duty cycle
        # Duty cycle = (pulse_width / period) * 100
        period = 1000000 / self.frequency  # period in microseconds
        duty_cycle = (pulse_width / period) * 100

        if self.debug:
            print(f"  [DEBUG] Angle {angle}° -> Pulse width {pulse_width:.0f}us -> Duty cycle {duty_cycle:.2f}%")

        return duty_cycle

    def set_angle(self, angle, hold_time=0.1):
        """
        Set servo to specific angle

        Args:
            angle: Target angle in degrees
            hold_time: Time to hold position (seconds)
        """
        # Clamp angle to valid range
        angle = max(self.min_angle, min(self.max_angle, angle))

        duty_cycle = self._angle_to_duty_cycle(angle)

        try:
            # lgpio.tx_pwm expects duty cycle as 0-100
            result = lgpio.tx_pwm(self.chip, self.pin, self.frequency, duty_cycle)
            if result < 0:
                print(f"ERROR: tx_pwm returned {result}")
            else:
                print(f"Servo set to {angle}°")

            # Give servo time to move
            time.sleep(hold_time)

            self.current_angle = angle
        except Exception as e:
            print(f"ERROR setting angle: {e}")

    def sweep(self, start_angle=None, end_angle=None, step=5, delay=0.05):
        """
        Sweep servo from start angle to end angle

        Args:
            start_angle: Starting angle (defaults to min_angle)
            end_angle: Ending angle (defaults to max_angle)
            step: Angle increment for each step
            delay: Delay between steps in seconds
        """
        if start_angle is None:
            start_angle = self.min_angle
        if end_angle is None:
            end_angle = self.max_angle

        print(f"Sweeping from {start_angle}° to {end_angle}°")

        if start_angle < end_angle:
            # Forward sweep
            for angle in range(start_angle, end_angle + 1, step):
                self.set_angle(angle, hold_time=delay)
        else:
            # Reverse sweep
            for angle in range(start_angle, end_angle - 1, -step):
                self.set_angle(angle, hold_time=delay)

    def center(self):
        """Move servo to center position"""
        center_angle = (self.min_angle + self.max_angle) / 2
        self.set_angle(center_angle)

    def off(self):
        """Turn off servo (stop sending pulses)"""
        try:
            lgpio.tx_pwm(self.chip, self.pin, 0, 0)
            print("Servo OFF (no pulses)")
        except Exception as e:
            print(f"ERROR turning off servo: {e}")

    def cleanup(self):
        """Clean up resources"""
        try:
            # Stop PWM
            lgpio.tx_pwm(self.chip, self.pin, 0, 0)
            # Close chip
            lgpio.gpiochip_close(self.chip)
            print("Servo cleanup complete")
        except Exception as e:
            print(f"ERROR during cleanup: {e}")


if __name__ == "__main__":
    """Test the servo controller"""
    print("=" * 50)
    print("SERVO CONTROLLER TEST (lgpio)")
    print("=" * 50)

    try:
        # Create servo controller
        # GPIO 18 = physical pin 12 (hardware PWM capable)
        print("\nInitializing servo...")
        servo = ServoController(
            pin=18,  # BCM GPIO 18 (physical pin 12)
            min_pulse_width=500,   # Extended range for digital servos
            max_pulse_width=2500,
            frequency=50,
            debug=True
        )

        # Wait for servo to initialize
        print("\nWaiting 2 seconds for servo to initialize...")
        time.sleep(2)

        # Simple back and forth test
        print("\n" + "=" * 50)
        print("SIMPLE BACK AND FORTH TEST (5 cycles)")
        print("=" * 50)

        for i in range(5):
            print(f"\nCycle {i+1}/5")

            # Move to 0 degrees
            print("  -> Moving to 0°")
            servo.set_angle(0, hold_time=0.8)

            # Move to 180 degrees
            print("  -> Moving to 180°")
            servo.set_angle(180, hold_time=0.8)

        # Return to center
        print("\n" + "=" * 50)
        print("Returning to center (90°)")
        servo.center()
        time.sleep(1)

        print("\nTest complete!")

    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\nERROR during test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        print("\nCleaning up...")
        try:
            servo.cleanup()
        except:
            pass
        print("Done!")
