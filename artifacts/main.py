# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from myo import Myo
import sys

last_pose = None

def printData(myo):
    global last_pose

    (roll_str, pitch_str, yaw_str) = ["*" * int(r) for r in myo.getRotationScaled(18.0)]

    arm_str=myo.getArmString()

    pose_str = myo.getPoseString()

    sys.stdout.write('\r[{:17s}][{:17s}][{:17s}][{:1s}][{:15s}]'.format(
        roll_str,
        pitch_str,
        yaw_str,
        arm_str,
        pose_str)
    )

    if(pose_str == "first") and (last_pose != myo.getPose()):
        myo.vibrate(Myo.VIBE_MEDIUM)

    last_post = myo.getPose()

def main():
    myMyo = Myo(callback=printData)
    myMyo.daemon = True
    myMyo.start()
    raw_input("Press enter to exit")

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()


