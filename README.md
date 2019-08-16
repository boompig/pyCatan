# Run

This is an implementation and visualization of Settlers of Catan in Python.
You can find the [rules for this game here][https://www.catan.com/files/downloads/catan_5th_ed_rules_eng_150303.pdf]

## Test

Use this to get a coverage report.

```
pytest catan --cov=catan --cov-report=html
```

## Disclaimer

WARNING: this code is very old.

I recently rediscovered this code and I am in the process of rehabilitating it

To run with Tkinter graphics, run

```
python catan_tk.py
```

There is a partially-implemented loading screen in `ui/load_screen.py`.

## JS UI

There is a partially-implemented javascript UI in `ui_mockup` folder. Run with `http-server` command and navigate to `catan_mockup.html`

## Game Features

The game is incomplete! To get specifics on what is implemented and what is not, see `progress.txt`.

## Keyboard Bindings

- escape - quits game
- return - ends turn
- space - ends turn