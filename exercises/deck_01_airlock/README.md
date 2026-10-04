# 🚪 Deck 01: The Airlock — "Pressure Drop"

> **Station time 03:12 · EMERGENCY STATE: RED**

## 📡 Mission Briefing

You are **Captain Roz**, alone in **Airlock Cabin A** of the *SS Traceback*.

The rescue capsule ***Kestrel*** has pulled alongside, carrying three crew
members who were stranded on the outer hull. But the capsule **won't lock**
onto the docking collar.

A micrometeor has cracked the collar and cabin pressure is bleeding out.
The impact also scrambled the sensor network: some sensors report garbage,
some have gone silent, and one is screaming an impossible value. The station's
control software crashes every time it hits a bad reading, so the automatic
docking sequence keeps aborting.

You have two problems to solve before the *Kestrel* runs out of air:

1. **The pressurisation error** — cabin pressure must be restored to a safe
   level, and right now the software can't even calculate it reliably.
2. **The airlock error** — all five docking clamps must confirm they are
   engaged. Some aren't. One isn't reporting at all.

Your only tool is the airlock's Python control module, `airlock.py`.
Rewrite it so it survives bad data, recovers pressure, and either docks
safely or fails loudly with a clear reason.

---

## 🎯 What you'll practise

- Handling different errors in **separate `except` blocks**
- Using **`else`** for code that should only run when nothing failed
- Using **`finally`** for safety cleanup that must always happen
- Re-raising an error with a **bare `raise`** after logging it
- **EAFP** vs **LBYL** coding styles

---

## 🛰️ Sensor Layout

### Pressure sensors (15)

| Ring | Sensors   | Location                         |
|------|-----------|----------------------------------|
| A    | P01–P05   | Inner cabin wall                 |
| B    | P06–P10   | Mid-cabin                        |
| C    | P11–P15   | Docking collar (near the breach) |

### Lock sensors (5)

One per docking clamp around the collar: **L1, L2, L3, L4, L5**.

The live readings from the moment of the emergency are in
`station_data.py`. Don't edit that file — it's the ship's real telemetry.

---

## 📋 Docking Rules

| Rule | Requirement |
|------|-------------|
| Valid reading | A number between **0 and 200 kPa** (inclusive) |
| Sensor quorum | At least **10 of 15** pressure sensors must be valid |
| Safe pressure | Average cabin pressure between **95 and 105 kPa** |
| Target pressure | Repressurise to **101.3 kPa** |
| Clamp seal | All **5 of 5** clamps must report `"engaged": True` |

---

## ⚠️ Ship Anomalies

These exceptions are already defined in `starship/errors.py`. Import and
use them — you don't need to write your own until Deck 03.

| Exception | Raised when | Useful attribute |
|-----------|-------------|------------------|
| `SensorFaultError` | Too few valid pressure sensors | `.faulty_sensors` |
| `PressureLossError` | Pressure unsafe or can't be restored | `.pressure` |
| `AirlockSealError` | One or more clamps not sealed | `.failed_clamps` |

All three inherit from `StarshipError`.

---

## 🛠️ Your Tasks

Open `airlock.py`. Each function has a docstring describing exactly what
it must do. Complete them in order — later functions use earlier ones.

### Task 1 · `parse_reading(raw)`
Turn one raw sensor value into a float, or `None` if it's faulty.
Handle `ValueError` and `TypeError` in **separate** `except` blocks, and do
the 0–200 range check in an **`else`** block.

### Task 2 · `cabin_pressure(readings)`
Average all valid readings. If fewer than 10 are valid, raise
`SensorFaultError` listing every faulty sensor ID, sorted.

### Task 3 · `verify_pressure(pressure)`
Raise `PressureLossError` if the pressure is outside the safe range.

### Task 4 · `repressurize(cabin)`
Open the reserve valve and bring the cabin up to 101.3 kPa.
If the reserve doesn't hold enough air, raise `PressureLossError` **without
changing** the cabin's pressure or reserve. The valve **must** be closed
afterwards, whatever happens.

### Task 5 · `check_clamps(lock_sensors)`
Confirm all five clamps are engaged using **EAFP** style: read the data
directly and handle the `KeyError`. A clamp fails if it's disengaged, has
no data, or is missing. Raise `AirlockSealError` listing every failed clamp
in L1–L5 order.

### Task 6 · `emergency_dock(pressure_readings, lock_sensors, cabin, incident_log)`
Run the full sequence: calculate pressure, repressurise if needed, then
check the clamps.
- On a seal failure, append `"SEAL FAILURE: <error message>"` to
  `incident_log`, then re-raise with a **bare `raise`**.
- Return `"DOCKED"` from an **`else`** block.
- In **`finally`**, always append `"Captain Roz: docking attempt logged"`.


### Task 7 · `starship/errors.py` — make errors readable
Add `__str__` and `__repr__` to all three exceptions.
`__str__` is what Captain Roz sees on the console. `__repr__` is what an
engineer sees in the debugger, and should look like the code that would
recreate the error. The exact formats are in the file's comments.

### Task 8 · Define two custom errors in `airlock.py`
Create `ReserveDepletedError` and `BreachDetectedError`. Both are kinds of
pressure loss, so any code that catches `PressureLossError` must still catch
them. Give each its own attributes, `__str__`, and `__repr__`.

### Task 9 · Put them to work
Upgrade `repressurize` to raise `ReserveDepletedError`, and write
`locate_breach` to find which sensor ring is losing pressure. With the live
data, it should point Roz straight to the docking collar.

> 🧠 **Try this in the REPL** once Task 7 passes:
> ```python
> >>> e = AirlockSealError(["L3", "L4"])
> >>> print(e)       # uses __str__
> >>> e              # uses __repr__
> >>> [e]            # containers always use __repr__
> ```
---
## 🧪 Run the Diagnostics

From the repo root:

```bash
python launch.py 01
```

Or from inside this folder:

```bash
python ../../launch.py
```

Every failing test name points to a specific requirement. Fix, rerun, repeat.

When all tests pass you'll see:

```
✅ Deck 01 systems restored. Proceed to the next deck, Engineer.
```

---

## 🎬 Watch the Scene

See your code handle the real emergency:

```bash
python demo.py
```

If your code is still broken, the demo crashes with a real traceback —
read it from the **bottom up** to find what failed and where.

---

## 🤔 Reflection: EAFP vs LBYL

Once your tests pass, try this (not graded):

Rewrite `check_clamps` in **LBYL** style ("Look Before You Leap") using
`if "engaged" in ...` checks instead of `try`/`except`.

- Which version is shorter and easier to read?
- If the sensor data came from a network call that could change *between*
  your check and your read, which version would still be correct?

Think about why Python code usually favours **EAFP** ("Easier to Ask
Forgiveness than Permission").

---

## ⭐ Extra Credit

1. Make `cabin_pressure` also report **which ring** has the lowest average
   pressure, so Roz knows where the breach is.
2. Add a `max_attempts` parameter to `emergency_dock` that retries the clamp
   check before giving up. Make sure the incident log still gets exactly one
   `"docking attempt logged"` entry per call.

---

## 💡 Stuck?

Check `hints.md` first. If you're still stuck, compare with
`solutions/deck_01_airlock/airlock.py` — but try every hint before you peek.

---

## 📚 Further Reading

- [Python Tutorial: Errors and Exceptions](https://docs.python.org/3/tutorial/errors.html)
- [Built-in Exceptions](https://docs.python.org/3/library/exceptions.html)
- [Glossary: EAFP](https://docs.python.org/3/glossary.html#term-EAFP) and
  [LBYL](https://docs.python.org/3/glossary.html#term-LBYL)
- [Real Python: Python Exceptions — An Introduction](https://realpython.com/python-exceptions/)

---