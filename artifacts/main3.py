from myo import init, Hub, Feed

init()
feed = Feed()
hub = Hub()
hub.run(1000, feed)

try:
  myo = feed.wait_for_single_device(timeout=2.0)
  if not myo:
    print("No Myo connected after 2 seconds")
  print("Hello, Myo!")
  while hub.running and myo.connected:
    quat = myo.orientation
    print('Orientation:', quat.x, quat.y, quat.z, quat.w)
finally:
  hub.shutdown()  # !! crucial