# LEGO slot:0 autostart
from hub import port, sound, button  # type: ignore
import runloop  # type: ignore
import color_sensor  # type: ignore
import distance_sensor  # type: ignore
import motor_pair  # type: ignore
import motor  # type: ignore
import math

# ==========================================
# 1. Hardware Configuration & Constants
# ==========================================
LEFT_MOTOR = port.C
RIGHT_MOTOR = port.D
SENSOR_PORT = port.B
DISTANCE_PORT = port.F
DIR_L = -1
DIR_R = 1
WHEEL_RADIUS = 2.82  # cm
TRACK_WIDTH = 11.5  # cm

# ==========================================
# 2. Odometry Core (Incremental Logic)
# ==========================================
def update_pose(x_i, y_i, theta_i_rad, prev_eL, prev_eR):
    """
    FUNCTION update_pose:
    // 1. GET NEW SENSOR DATA
    READ current degrees from Left Motor and Right Motor
    // 2. CALCULATE WHEEL MOVEMENT
    COMPUTE how many centimeters the Left Wheel moved since last check
    COMPUTE how many centimeters the Right Wheel moved since last check
    // 3. CALCULATE ROBOT MOVEMENT
    // Forward movement
    // Turning
    // 4. UPDATE GLOBAL POSITION (X, Y, Angle)
    UPDATE the X coordinate (using Forward_Distance and current angle)
    UPDATE the Y coordinate (using Forward_Distance and current angle)
    UPDATE the Robot's Angle (adding the Change_in_Angle)
    // 5. FINISH
    RETURN the new X, Y, Angle, and the current motor degrees for the next loop
    """
    # Get current encoder values
    curr_eL = motor.relative_position(LEFT_MOTOR) * DIR_L
    curr_eR = motor.relative_position(RIGHT_MOTOR) * DIR_R

    # Calculate wheel distances (degrees to cm)
    delta_L = (curr_eL - prev_eL) * (math.pi / 180) * WHEEL_RADIUS
    delta_R = (curr_eR - prev_eR) * (math.pi / 180) * WHEEL_RADIUS

    # Calculate forward movement and rotation
    forward_dist = (delta_L + delta_R) / 2
    delta_theta = (delta_R - delta_L) / TRACK_WIDTH

    # Update pose
    x_i += forward_dist * math.cos(theta_i_rad + delta_theta / 2)
    y_i += forward_dist * math.sin(theta_i_rad + delta_theta / 2)
    theta_i_rad += delta_theta

    return x_i, y_i, theta_i_rad, curr_eL, curr_eR

# ==========================================
# 3. Main Routine
# ==========================================
# async def main():
        
#     # State Definitions
#     FORWARD = "ForwardMovement"
#     BACKWARD = "BackwardMovement"
#     IDLE = "Idle"

#     state = FORWARD

#     motor_pair.pair(motor_pair.PAIR_1, LEFT_MOTOR, RIGHT_MOTOR)
#     # Set the robot's starting position (X, Y) and angle (Theta) to zero.
#     # This is the origin point (0,0) on our invisible map.
#     x_pos, y_pos, theta_rad = 0.0, 0.0, 0.0

#     prev_eL = motor.relative_position(LEFT_MOTOR) * DIR_L
#     prev_eR = motor.relative_position(RIGHT_MOTOR) * DIR_R
    
#     while True:

#         TARGET_DIST = 20
#         dist = distance_sensor.distance(DISTANCE_PORT)

#         # Handle "no object detected"
#         if dist == -1:
#             dist = 2000  # treat as very far

#         # Too far → move forward
#         if dist > TARGET_DIST + 1:
#             state = FORWARD

#         # Too close → move backward
#         elif dist < TARGET_DIST - 1:
#             state = BACKWARD
#         # Within comfort zone → stop
#         else:
#             state = IDLE

#         # # Print only when state changes
#         # if new_state != state:
#         #     state = new_state
#         #     print("State:", state)

#         # Inside the main loop:
#         if state == FORWARD:
#            motor_pair.move(motor_pair.PAIR_1, 0, velocity=120)
#         elif state == BACKWARD:
#             motor_pair.move(motor_pair.PAIR_1, 0, velocity=-120)
#         elif state == IDLE:
#             motor_pair.stop(motor_pair.PAIR_1)

#         print("Distance:", dist, "State:", state)

async def main():
    # ---------------------------------------------------------
    # INITIALIZATION
    # ---------------------------------------------------------
    motor_pair.pair(motor_pair.PAIR_1, LEFT_MOTOR, RIGHT_MOTOR)

    TARGET_DIST = 200      # cm
    TOL = 10               # deadband to avoid jitter

    IDLE = "Idle"
    FORWARD = "ForwardMovement"
    BACKWARD = "BackwardMovement"

    state = IDLE
    print("State:", state)

    # ---------------------------------------------------------
    # MAIN LOOP
    # ---------------------------------------------------------
    while True:

        dist = distance_sensor.distance(DISTANCE_PORT)

        # Handle no object detected
        if dist == -1:
            dist = 2000  # treat as very far

        # =====================================================
        # STATE TRANSITIONS
        # =====================================================

        # Too far: move forward
        if dist > TARGET_DIST + TOL:
            new_state = FORWARD

        # Too close: move backward
        elif dist < TARGET_DIST - TOL:
            new_state = BACKWARD

        # Within comfort zone: stop
        else:
            new_state = IDLE

        # Print only when state changes
        if new_state != state:
            state = new_state
            print("State:", state)

        # =====================================================
        # STATE ACTIONS
        # =====================================================

        if state == FORWARD:
            motor_pair.move(motor_pair.PAIR_1, 0, velocity=120)

        elif state == BACKWARD:
            motor_pair.move(motor_pair.PAIR_1, 0, velocity=-120)

        elif state == IDLE:
            motor_pair.stop(motor_pair.PAIR_1)

        await runloop.sleep_ms(50)

# Start the asynchronous event loop to run the main function
runloop.run(main())