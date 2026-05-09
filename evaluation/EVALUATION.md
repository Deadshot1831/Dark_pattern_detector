# DeceptiTech Detector Evaluation

Source: `dark-patterns-v2.csv` — 1818 total rows. 306 rows have no `Pattern String` (only behaviour comments like "Sale. Resets on each load." with no captured on-page text), so **1512 rows are evaluable**.

## Scope

Only text-based detectors are evaluated (urgency, scarcity, confirmshaming). The DOM-based detectors (preselected options, cookie manipulation) need rendered HTML that this CSV doesn't carry — they're verified separately by the unit fixture in `backend/tests/test_detectors.py` (9-invariant assertion test, all passing).

## Results

| Detector | TP | FP | FN | TN | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|---:|
| `fake_urgency` | 218 | 114 | 19 | 1161 |  65.7% |  92.0% |  76.6% |
| `scarcity` | 520 | 37 | 158 | 797 |  93.4% |  76.7% |  84.2% |
| `confirmshaming` | 124 | 0 | 45 | 1343 | 100.0% |  73.4% |  84.6% |
| **macro avg** |  |  |  |  | ** 86.3%** | ** 80.7%** | ** 81.8%** |

## Mapping (our detector → CSV `Pattern Type`)

- **fake_urgency** ← `Countdown Timer` (149), `Limited-time Message` (88)  ·  total positive examples: 237
- **scarcity** ← `Low-stock Message` (631), `High-demand Message` (47)  ·  total positive examples: 678
- **confirmshaming** ← `Confirmshaming` (169)  ·  total positive examples: 169

## Notes on cross-pattern overlap

Some dataset texts are simultaneously urgent *and* scarce (e.g. `Hurry, only 2 left in stock!`). Each row has a single label, so the detector that doesn't own that label scores a false positive — this slightly understates precision. The error tables below make this visible: most cross-pattern FPs are texts that legitimately match more than one dark-pattern category.

## `fake_urgency` — error analysis

### Top false positives (15 shown)

- *(labelled `Activity Notification`)* — Hurry up! 6 people other than you have this product in their cart
- *(labelled `Activity Notification`)* — Hurry up! 22 people other than you have this product in their cart
- *(labelled `Activity Notification`)* — Don't miss out! We've sold 38 in the last few days.
- *(labelled `High-demand Message`)* — Our items sell fast, don't miss out!
- *(labelled `High-demand Message`)* — Hurry, this style is selling fast!
- *(labelled `High-demand Message`)* — Due To HIGH Demand, Cart Expires In: 08:41
- *(labelled `High-demand Message`)* — Hurry, this style is selling fast!
- *(labelled `Low-stock Message`)* — 894 Claimed! Hurry, only a few left!
- *(labelled `Low-stock Message`)* — 89% offers claimed. Hurry up!
- *(labelled `Low-stock Message`)* — HURRY! ONLY 19 LEFT IN STOCK.
- *(labelled `Low-stock Message`)* — 70% offers claimed. Hurry up!
- *(labelled `Low-stock Message`)* — Hurry, only 3 left!
- *(labelled `Low-stock Message`)* — HURRY! Only a few left in stock!
- *(labelled `Low-stock Message`)* — 80% offers claimed. Hurry up!
- *(labelled `Low-stock Message`)* — 70% offers claimed. Hurry up!

### Top false negatives (15 shown)

- *(labelled `Countdown Timer`)* — 00DAYS02HRS14MINS1211SEC
- *(labelled `Countdown Timer`)* — 00DAYS00HOURS14MINUTES21SECONDS
- *(labelled `Countdown Timer`)* — 0 DAYS22 HOURS13 MINUTES21 SECONDS
- *(labelled `Countdown Timer`)* — 00DAYS07HOURS09MINUTES39SECONDS
- *(labelled `Countdown Timer`)* — SAVE $200 OFF PUFFY
- *(labelled `Countdown Timer`)* — 11 11 Hours: 00 22 Minutes: 3223 3223 Seconds
- *(labelled `Countdown Timer`)* — 00Days17Hours12Mins13Secs
- *(labelled `Countdown Timer`)* — Spring Sale Extended
- *(labelled `Countdown Timer`)* — 3DAYS124606
- *(labelled `Countdown Timer`)* — 3DAYS124606
- *(labelled `Countdown Timer`)* — Flash Sale - Almost Over! 00 HOURS : 55 1001 MINUTES : 0550 8778 SECONDS
- *(labelled `Countdown Timer`)* — DAYS HRS MINS SECS
- *(labelled `Countdown Timer`)* — Your order has been reserved for
- *(labelled `Countdown Timer`)* — Price Guaranteed For DAYS/HRS/MINS/SECS
- *(labelled `Limited-time Message`)* — LIMITED OFFER: $125 Off + 2 Free Pillows

## `scarcity` — error analysis

### Top false positives (15 shown)

- *(labelled `Activity Notification`)* — 9 people are viewing this.
- *(labelled `Activity Notification`)* — 5338 people viewed this in the last hour
- *(labelled `Activity Notification`)* — 3 people bought this item last week.
- *(labelled `Activity Notification`)* — 2 people are looking at this listing now
- *(labelled `Activity Notification`)* — 38 people are viewing this
- *(labelled `Activity Notification`)* — 64 users bought this product Touch: The Set - Touch XL & TouchUp Makeup Mirror Bundle
- *(labelled `Activity Notification`)* — 🔥 9 people are viewing this.
- *(labelled `Activity Notification`)* — 3 people are looking at this product
- *(labelled `Activity Notification`)* — Popular Item! 🔥 16 people are viewing this and 18 recently purchased it.
- *(labelled `Activity Notification`)* — 23 People viewing this product
- *(labelled `Activity Notification`)* — 8 people are looking at this artwork
- *(labelled `Activity Notification`)* — 104 people viewed this product recently!
- *(labelled `Activity Notification`)* — 5 people are looking at this product right now
- *(labelled `Activity Notification`)* — 19 people viewed this product per day
- *(labelled `Activity Notification`)* — 3 PEOPLE VIEWING

### Top false negatives (15 shown)

- *(labelled `High-demand Message`)* — Strong demand! Complete your order before it's too late!
- *(labelled `High-demand Message`)* — Items in your cart are in VERY high-demand.
- *(labelled `High-demand Message`)* — Sorry, this is out of stock. You just missed it.
- *(labelled `High-demand Message`)* — Our items sell fast, don't miss out!
- *(labelled `High-demand Message`)* — In demand
- *(labelled `Low-stock Message`)* — Only 2 units left in stock
- *(labelled `Low-stock Message`)* — 4 items left
- *(labelled `Low-stock Message`)* — Low In Stock Today
- *(labelled `Low-stock Message`)* — Only 1 unit left in stock
- *(labelled `Low-stock Message`)* — 89% offers claimed. Hurry up!
- *(labelled `Low-stock Message`)* — 70% offers claimed. Hurry up!
- *(labelled `Low-stock Message`)* — 96 ITEM(S) LEFT IN STOCK!
- *(labelled `Low-stock Message`)* — Availability: Low in stock today
- *(labelled `Low-stock Message`)* — Limited Quantity
- *(labelled `Low-stock Message`)* — 80% offers claimed. Hurry up!

## `confirmshaming` — error analysis

### Top false positives (0 shown)

_None._

### Top false negatives (15 shown)

- *(labelled `Confirmshaming`)* — No thanks! I don't like deals
- *(labelled `Confirmshaming`)* — No, I'll rather pay full price.
- *(labelled `Confirmshaming`)* — No, thanks. I don't like great deals.
- *(labelled `Confirmshaming`)* — No Thanks, I rather pay full price
- *(labelled `Confirmshaming`)* — No thanks, I’ll skip this amazing super-saver deal. I don’t need so many beautiful textures
- *(labelled `Confirmshaming`)* — No thanks, I despise coupons!
- *(labelled `Confirmshaming`)* — I WANT TO PAY MORE LATER ;)
- *(labelled `Confirmshaming`)* — I do not want to protect my item
- *(labelled `Confirmshaming`)* — No, thanks, I´d rather pay more
- *(labelled `Confirmshaming`)* — NO, I'D RATHER PAY FULL PRICE
- *(labelled `Confirmshaming`)* — I'd rather not save
- *(labelled `Confirmshaming`)* — No thanks, I’d rather pay full price.
- *(labelled `Confirmshaming`)* — No thanks, I don’t like fun and games.
- *(labelled `Confirmshaming`)* — No, I'd rather do it the hard way...
- *(labelled `Confirmshaming`)* — NO THANKS, I DON’T MIND MISSING OUT

