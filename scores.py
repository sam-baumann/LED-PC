import sys, math, datetime, urllib, json, atexit, time, os
import RPi.GPIO as GPIO

def load(teamId):
  now = datetime.datetime.now()
  date = str(now.year)+"-"+str(now.month)+"-"+str(now.day)
  url = "https://statsapi.web.nhl.com/api/v1/schedule?startDate="+date+"&endDate="+date+"&expand=schedule.teams,schedule.linescore,schedule.game&leaderCategories=&site=en_nhl&teamId="+str(teamId)
  jsonRaw = urllib.urlopen(url).read().decode("utf-8")
  json1 = json.loads(jsonRaw)
  try:
    games = json1["dates"][0]["games"][0]
  except IndexError:
    print(date)
    return "No games today!"
  print("loaded")
  return games
  
def pulse(hawksGame):
  if hawksGame:
    os.system("omxplayer chicago.mp3 &")
  else:
    os.system("omxplayer horn.mp3 &")
  
  time.sleep(3)
  dc = 0
  start = time.time()
  elapsed = 0
  x = 0
  pin = 22
  GPIO.setmode(GPIO.BCM)
  GPIO.setup(pin, GPIO.OUT)
  p = GPIO.PWM(pin, 50)
  p.start(dc)
  while elapsed <= 10:
    dc = ((math.sin(math.pi*elapsed)/2) + .5)*100
    p.ChangeDutyCycle(dc)
    time.sleep(0.01)
    elapsed = time.time() - start
  for duty in range(int(dc), 0, -1):
    p.ChangeDutyCycle(float(duty))
    time.sleep(0.01)
  p.stop()
  GPIO.cleanup()
  
def score_checker(teamID):
  time.sleep(60)
  homeTeam = False
  baseHomeTeamScore = 0
  baseAwayTeamScore = 0
  hawksGame = False
  while 1:
    try:
      jsonFull = load(teamID)
    except:
      continue
    jsonScores = jsonFull["teams"]
    homeTeamScore = jsonScores["home"]["score"]
    awayTeamScore = jsonScores["away"]["score"]
    if jsonScores["home"]["team"]["id"] == int(teamID):
      homeTeam = True
    if homeTeam:
      if jsonScores["away"]["team"]["id"] == 16:
        hawksGame = True
    else:
      if jsonScores["home"]["team"]["id"] == 16:
        hawksGame = True
    if jsonFull["status"]["abstractGameState"] == "Live":
      if homeTeam and (homeTeamScore != baseHomeTeamScore):
        try:
          pulse(hawksGame)
        except KeyboardInterrupt:
          GPIO.PWM(22, 40).stop()
          GPIO.cleanup()
        baseHomeTeamScore = homeTeamScore
        print("score!")
      elif (homeTeam == False) and (awayTeamScore != baseAwayTeamScore):      
        try:
          pulse(hawksGame)
        except KeyboardInterrupt:
          GPIO.PWM(22, 40).stop()
          GPIO.cleanup()
        baseAwayTeamScore = awayTeamScore
        print("score!")
      else:
        print(str(homeTeamScore) + "," + str(baseHomeTeamScore))
        print(str(awayTeamScore) + "," + str(baseAwayTeamScore))
        print(homeTeam)
        print("home team id:" + str(jsonScores["home"]["team"]["id"]))
        time.sleep(10)
    else:
      print("game not started, sleeping for 10 minutes")
      time.sleep(300)
      print("5 minutes left")
      time.sleep(300)
  
  
if __name__ == "__main__":
  score_checker(sys.argv[1])
  
  
  
  
  
  
  