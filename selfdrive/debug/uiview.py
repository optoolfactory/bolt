#!/usr/bin/env python3
import time
from multiprocessing import Process
from cereal import messaging, log
from selfdrive.manager.process_config import managed_processes
from selfdrive.manager.process import launcher

if __name__ == "__main__":

  road_speed_limiter = Process(name="road_speed_limiter", target=launcher, args=("selfdrive.road_speed_limiter",))
  road_speed_limiter.start()

  procs = ['camerad', 'ui', 'modeld', 'calibrationd']

  for p in procs:
    managed_processes[p].start()

  pm = messaging.PubMaster(['controlsState', 'deviceState', 'pandaStates', 'carParams'])

  msgs = {s: messaging.new_message(s) for s in ['controlsState', 'deviceState', 'carParams']}
  msgs['deviceState'].deviceState.started = True
  msgs['carParams'].carParams.openpilotLongitudinalControl = True

  msgs['pandaStates'] = messaging.new_message('pandaStates', 1)
  msgs['pandaStates'].pandaStates[0].ignitionLine = True
  msgs['pandaStates'].pandaStates[0].pandaType = log.PandaState.PandaType.uno

  try:
    while True:
      time.sleep(1 / 100)  # continually send, rate doesn't matter
      for s in msgs:
        pm.send(s, msgs[s])
  except KeyboardInterrupt:
    for p in procs:
      managed_processes[p].stop()

    road_speed_limiter.terminate()
