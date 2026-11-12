import csv

new_rows = [
  # 7 Chinese list episodes (high CTR format)
  ("CN-LIST01", "Top 7 Demon Cultivators Who Met Their End", "Every demon rewrites the rules they swore to obey - discipline outlasts fear", "chinese"),
  ("CN-LIST02", "Top 8 Most Savage Betrayals in Cultivation History", "Even the purest tao decays without vigilance - keep your teacher suspect", "chinese"),
  ("CN-LIST03", "Top 5 Strongest Sword Masters Who Were Actually Very Weak", "Raw speed is a peasant's tool - patience is the sword's dragon", "chinese"),
  ("CN-LIST04", "Top 9 Rogue-Clan Geniuses Hidden Among Farmers", "Genius wears mud not silk - watch the humble before the noble", "chinese"),
  ("CN-LIST05", "Top 6 Most Generous Palace Servants Who Became Kings", "True kings are built from service - duty precedes crown", "chinese"),
  ("CN-LIST06", "Top 10 Arrogant Heirs Who Were Humbled Overnight", "Pride drinks first but pays last - hubris earns its day", "chinese"),
  ("CN-LIST07", "Top 4 Blade Masters Who Couldn't Lift a Rock", "Sheer muscle never elevated a man; blade answers mind, not arm", "chinese"),
  # 6 Japanese list episodes
  ("JP-LIST01", "Top 10 Quietest Schoolgirls Who Were the Legend", "True legends never introduce themselves; they arrive", "japanese"),
  ("JP-LIST02", "Top 8 Heirs Who Cheated Themselves Out of Survival", "Time is the only justice; patience pays compound interest", "japanese"),
  ("JP-LIST03", "Top 9 Japanese 2D Anime Villains Nobody Saw Coming", "Whatever you are about to do, the heavens are watching too", "japanese"),
  ("JP-LIST04", "Top 9 Most Misunderstood Samurai in 100 Years", "Mercy and cruelty both wound - who chooses separates them", "japanese"),
  ("JP-LIST05", "Top 5 Quiet Girls Who Suddenly Stole the Scene", "Destiny favors the quietly prepared - silence is a riot", "japanese"),
  ("JP-LIST06", "Top 7 Destined Shields of the Weak", "True heroism enters without asking - valor has no introduction", "japanese"),
]

with open("episodes_100.csv", "a", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    for row_id, topic, moral, track in new_rows:
        w.writerow([row_id, topic, moral, track])

with open("episodes_100.csv", "r", encoding="utf-8") as f:
    lines = f.readlines()
print("total rows (including header):", len(lines))
print("new last row:", lines[-1].strip())
