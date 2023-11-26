import tkinter as tk
from tkinter import Frame, Button, Label

def launch_eye_tracking_program():
    exec(open('ET_v2.1.py').read())

def launch_check_the_pictures():
    exec(open('CheckThePictures.py').read())

def launch_driver_safety_simulation():
    exec(open('DriverSafetySimulation.py').read())

app = tk.Tk()
app.title("Eye Tracking App")
app.geometry("800x600")

app.configure(bg="lightgreen")
main_frame = Frame(app, bg="lightgreen")
main_frame.place(relwidth=1, relheight=1)

title_label = Label(main_frame, text="Select an option", bg="lightgreen", font=("Helvetica", 24))
title_label.pack(pady=20)

# Buttons to launch programs
button1 = Button(main_frame, text="Eye Tracking Program", bg="green", fg="white", font=("Helvetica", 18), width=20,
                 command=launch_eye_tracking_program)
button1.pack(pady=10)
button1_desc = Label(main_frame, text="Explore eye tracking technology!", bg="lightgreen", font=("Helvetica", 12))
button1_desc.pack()

button2 = Button(main_frame, text="Test the pictures", bg="green", fg="white", font=("Helvetica", 18), width=20,
                 command=launch_check_the_pictures)
button2.pack(pady=10)
button2_desc = Label(main_frame, text="See where your attention is when looking at a picure!", bg="lightgreen",
                     font=("Helvetica", 12))
button2_desc.pack()

button3 = Button(main_frame, text="Driver Safety Simulation", bg="green", fg="white", font=("Helvetica", 18), width=20,
                 command=launch_driver_safety_simulation)
button3.pack(pady=10)
button3_desc = Label(main_frame, text="Experience driver safety simulation!", bg="lightgreen", font=("Helvetica", 12))
button3_desc.pack()

def bring_app_to_front():
    app.lift()
    app.attributes('-topmost', 1)
    app.attributes('-topmost', 0)

# GUI main loop
app.mainloop()