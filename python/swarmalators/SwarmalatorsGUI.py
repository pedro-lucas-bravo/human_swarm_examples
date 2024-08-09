import tkinter as tk
from tkinter import ttk

# START: Events for external communication
OnButtonClickedEvent = None
OnCloseWindowEvent = None
OnKnobChangedEvent = None
# END: Events for external communication

def button_click(id):
    if OnButtonClickedEvent is not None:
        OnButtonClickedEvent(id)

def knob_changed(value, id, label, type):
    if type == 'int':
        rounded_value = int(float(value))
    else:
        rounded_value = round(float(value), 2)
    label['text'] = rounded_value
    if OnKnobChangedEvent is not None:
        OnKnobChangedEvent(id, rounded_value)

def slider_changed(value):
    print("Slider value changed:", value)

def close_window():
    if OnCloseWindowEvent is not None:
        OnCloseWindowEvent()
    root.destroy()

#Global root
root = tk.Tk()
knobs = []

def SwarmalatorsGUI_Define(init_N, init_J, init_K, init_Speed, init_interactive_N):
    global root
    global knobs

    #Print message when GUI closes, call close_window function
    root.protocol("WM_DELETE_WINDOW", close_window)

    root.title("Music Controller")

    # Buttons

    button_frame = ttk.Frame(root, borderwidth=2, relief="solid")
    button_frame.pack(pady=10)

    button_title = ttk.Label(button_frame, text="States", font=("Arial", 10, "bold"), justify='left')
    button_title.grid(row=0, column=0, padx=5)

    swarmalators_states = ['static sync', 'static async', 'static phase wave', 'splintered phase wave', 'active phase wave'] 

    for i in range(5):
        button = ttk.Button(button_frame, text=swarmalators_states[i], command=lambda id=i+1: button_click(id))
        button.grid(row=1, column=i, padx=5)

    # Knobs
    N_knobs = 5

    knob_frame = ttk.Frame(root)
    knob_frame.pack(pady=10)

    knob_params = ['N', 'J', 'K', 'Speed', 'Interactive N']
    knob_values = [init_N, init_J, init_K, init_Speed, init_interactive_N]
    knob_from = [1, -1, -1, 1, 0]
    knob_to = [200, 1, 1, 20, 10]
    knob_types = ['int', 'float', 'float', 'float', 'int']
    for i in range(N_knobs):
        label = ttk.Label(knob_frame, text=knob_params[i], anchor="e")
        label.grid(row=i, column=1, padx=5)
        slider_value = tk.StringVar()
        slider_value.set(knob_values[i])
        slider_label = ttk.Label(knob_frame, width=10)
        slider_label.grid(row=i, column=2, padx=5)
        slider_label['text'] = knob_values[i]
        knob = ttk.Scale(knob_frame, from_=knob_from[i], to=knob_to[i], variable=slider_value, command=lambda val = slider_value.get(), id=i+1, label = slider_label, type = knob_types[i]: knob_changed(val, id, label, type), orient="horizontal", length=200, style="TScale")
        knob.grid(row=i, column=0, padx=10)
        knobs.append(knob)

def SwarmalatorsGUI_Set_J_K(j, k):
    global knobs
    knobs[1].set(j)
    knobs[2].set(k)

def SwarmalatorsGUI_Run():
    global root
    root.mainloop()