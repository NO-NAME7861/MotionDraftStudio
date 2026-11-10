import csv, json
rows = []
# 1) Chinese track (from episodes.csv, 001 already uploaded manually)
with open('episodes.csv', encoding='utf-8') as f:
    for r in csv.DictReader(f):
        if r['id'] == '001':
            rows.append({'topic': r['topic'], 'moral': r['moral'], 'track': 'chinese'})
        else:
            rows.append({'topic': r['topic'], 'moral': r['moral'], 'track': 'chinese'})
with open('arc_poisoned_son.csv', encoding='utf-8') as f:
    for r in csv.DictReader(f):
        rows.append({'topic': r['topic'], 'moral': r['moral'], 'track': 'chinese'})
# 2) Japanese track (from season2_japanese.csv)
with open('season2_japanese.csv', encoding='utf-8') as f:
    for r in csv.DictReader(f):
        rows.append({'topic': r['topic'], 'moral': r['moral'], 'track': 'japanese'})

new_chinese = [
    ("The Blade Emperor Who Broke His Own Throne For Peace", "Power renounced for peace is the greatest victory"),
    ("The Immortal Sword Saint Who Chose Silence Over the War", "Silence disarms more than steel; restraint is real strength"),
    ("The Merchant Who Sold His Fortune To Rescue A Clan", "Wealth spent well buys eternal memory; hoarding buys nothing"),
    ("The Orphan Cultivator Who Refused the Dark Path", "Power without principle is monstrous; virtue is the real power"),
    ("The Azure Dragon's Apprentice Who Faced His Master's Betrayal", "Loyalty tested reveals what loyalty meant; honesty outlasts betrayal"),
    ("The Heavenly Fox Who Traded Immortality For His Daughter", "Some sacrifices are priceless; love outranks eternal life"),
    ("The Wounded Archer Who Never Missed on the Battlefield", "Focus born of pain defeats raw skill; adversity sharpens purpose"),
    ("The Poisoned Duke Who Forgave The Man Who Poisoned Him", "Forgiveness disarms the poisoner; revenge only mutates the poison"),
    ("The Palace Servant Who Rose to Become Emperor of the Realm", "Humble service rises farther than ruthless ambition"),
    ("The Sword Cultivator Who Refused the Demon King's Throne", "The crown is a trap; freeing yourself from it is freedom itself"),
    ("The Fallen Warrior Reborn as a Farmer Who Planted a Kingdom", "Seeds grow where swords cannot; patience builds empires"),
    ("The Exiled Prince Who Tamed the Wild Beast of Heaven", "Taming beasts within must come before taming the world"),
    ("The Archer Saint Who Taught His Enemy to Breathe Again", "Even your enemy deserves breath; compassion widens the world"),
    ("The Healer Who Saved the Soldier Who Wounded Her", "Mercy heals even the one who hurt you; kindness circles back"),
    ("The Rice Merchant Who Fed a Plague City at His Own Cost", "Feeding others is never wasted; compassion beats profit every time"),
    ("The Blade Saint Who Vowed Never to Draw His Sword Again", "A sword unsheathed is a sword doomed; restraint is nobleness"),
    ("The Demon Hunter Who Spared the Last Demon In the Realm", "Mercy to the defeated preserves what war destroys"),
    ("The Cultivator Who Sold His Soul and Later Bought It Back", "Some debts can be repaid; some can only be carried"),
    ("The Mountain Hermit Who Taught the Warlord What Peace Meant", "Real power is leaving war behind; peace is the hardest discipline"),
    ("The Warrior Who Defeated the Heavenly Emperor Single-Handedly", "One disciplined mind can unseat the world; imagination is the real blade"),
]

new_japanese = [
    ("The Salaryman Reborn as a Merchant of Spirit Rings", "Work with integrity earns more than shortcuts; character compounds"),
    ("The Shrine Maiden Who Outsmarted the Fox God With Rice Wine", "Simple goodwill beats towering trickery"),
    ("The Basketball Star Who Lost Everything and Found His Path", "Failure is a teacher; what you lose is a gift in disguise"),
    ("The Heiress Who Abandoned Her Housewealth for Love", "Family without love is a hollow treasury; a house's true worth is warmth"),
    ("The Ninja Who Loves His Enemy's Daughter Without Knowing", "Love without identity is still love; dignity refuses manipulation"),
    ("The Tycoon Who Realized He Worked Himself Hollow", "No amount of gold buys back a life; regret teaches late but true"),
    ("The Chef Who Became a Wandering Hermit in the Mountains", "Simplicity is the last wealth; humility lets skill speak"),
    ("The Samurai Who Broke His Lord's Law to Save His Village", "Justice above law; humanity over hierarchy"),
    ("The Idol Singer Who Abandoned Fame for Her Grandmother", "Family outweighs fame; grace outweighs glitter"),
    ("The Demon Lord's Daughter Who Wanted to Be an Ordinary Girl", "Legacy is a burden only if you carry it unwillingly; choose freedom"),
    ("The Rooftop Scholar Who Solved the Mystery of the City's Plague", "Keen observation saves more than brute force"),
    ("The Exiled General Who Rebuilt His Samurai Army From Scratch", "True strength grows from loss; rebuilding is the hardest art"),
    ("The Student Who Refused to Cheat Though the Whole School Cheated", "Integrity when it costs you everything is the highest grade"),
    ("The Desert Fox Who Inherited the Clan but Lost His Heart", "Loyalty without love is just duty; balance both or lose both"),
    ("The Woman Who Inherited the Samurai Mansion in Silence", "Quiet stewardship outlasts loud ambition"),
    ("The Violinist Who Played For the Dying Tycoon Night After Night", "Music softens what wealth cannot; art cures harder than medicine"),
    ("The Blade Apprentice Who Beat His Master in a Fair Duel", "Earning victory through discipline honors the teacher more than obedience"),
    ("The Heavenly Cultivator Who Abandoned Immortality For His Daughter", "Mortality is a blessing; eternal life without loved ones is hell"),
    ("The Last Samurai Who Guarded the Old Castle Alone for Ten Years", "Duty fulfilled silently is the rarest nobility"),
    ("The Tattooed Rebel Who Carried His Clan's Shame and Made It Beauty", "A shame transformed is a gift; redemption begins with acceptance"),
    ("The Emperor Who Asked His Enemy What He Would Do With Peace", "Listening to your enemy may teach you how to keep peace"),
    ("The Blademaster Who Chose Not to Strike the Younger Opponent", "Choosing not to strike is the hardest blow; control is true mastery"),
    ("The Rogue Merchant Who Sold His Life's Work to Save His Apprentice", "Sacrifice is not loss; it is the deepest wealth"),
    ("The Tea Master Who Realized Serving Tea Is Serving the World", "Every act done fully is a world; small rituals are great practices"),
    ("The Snow Country Swordsman Who Trained His Daughter Into Legend", "Raising the next generation in honor is immortality of the soul"),
    ("The Fisherman's Son Who Became the Emperor of the Valley", "Nobility flows in blood only; in courage it flows in anyone"),
    ("The Weaver's Daughter Who Saved Her Village With a Cloth", "Small crafts can hold great journeys; patience weaves more than thread"),
]

for topic, moral in new_chinese:
    rows.append({'topic': topic, 'moral': moral, 'track': 'chinese'})
for topic, moral in new_japanese:
    rows.append({'topic': topic, 'moral': moral, 'track': 'japanese'})

chinese = [r for r in rows if r['track'] == 'chinese']
japanese = [r for r in rows if r['track'] == 'japanese']
print('chinese:', len(chinese), 'japanese:', len(japanese), 'total:', len(rows))

# Interleave CN and JP in the master CSV: 001-CN, 002-JP, ...
m = []
ci = ji = 0
i = 1
while ci < len(chinese) or ji < len(japanese):
    if ci < len(chinese):
        r = chinese[ci]; ci += 1
        m.append({'id': str(i), 'topic': r['topic'], 'moral': r['moral'], 'track': 'chinese'}); i += 1
    if ji < len(japanese):
        r = japanese[ji]; ji += 1
        m.append({'id': str(i), 'topic': r['topic'], 'moral': r['moral'], 'track': 'japanese'}); i += 1

with open('episodes_100.csv', 'w', encoding='utf-8', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['id','topic','moral','track'])
    w.writeheader()
    w.writerows(m)

print('wrote', len(m), 'rows to episodes_100.csv')
from collections import Counter
print(Counter(r['track'] for r in m))
# unique topics check
assert len(set(r['topic'] for r in m)) == len(m), 'duplicate topics!'
print('topics unique: OK')
