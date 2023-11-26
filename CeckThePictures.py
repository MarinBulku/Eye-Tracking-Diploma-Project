import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2
from Objects_Methods.gaze_tacking import GazeTracking

class PictureViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Picture Viewer")
        self.root.geometry("800x600")
        self.root.configure(bg="lightgreen")

        self.image_list = []
        self.current_image_idx = 0

        self.load_images_button = tk.Button(self.root, text="Load Pictures", command=self.load_pictures)
        self.load_images_button.pack(pady=20)
        self.load_images_button.configure(bg="green", fg="white", padx=10, pady=5, font=("Helvetica", 14))

        self.canvas = tk.Canvas(self.root, width=600, height=400, bg="white")
        self.canvas.pack()

        self.prev_button = tk.Button(self.root, text="Previous", command=self.show_previous_picture, state="disabled")
        self.prev_button.pack(pady=10)
        self.prev_button.configure(bg="green", fg="white", padx=10, pady=5, font=("Helvetica", 14))

        self.next_button = tk.Button(self.root, text="Next", command=self.show_next_picture, state="disabled")
        self.next_button.pack(pady=10)
        self.next_button.configure(bg="green", fg="white", padx=10, pady=5, font=("Helvetica", 14))

        # Create a GazeTracking instance
        self.gaze = GazeTracking()
        self.webcam = cv2.VideoCapture(0)
        self.gaze_coords = None  # Store gaze coordinates
        self.track_gaze()  # Start continuous gaze tracking
        self.update_gaze() # Start updating gaze coordinates

    def load_pictures(self):
        file_paths = filedialog.askopenfilenames(title="Select the pictures",
                     filetypes=(("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*")))

        if file_paths:
            self.image_list = [Image.open(file_path) for file_path in file_paths]
            self.current_image_idx = 0
            self.show_current_picture(self.gaze_coords)
            self.update_button_states()


    def update_gaze(self):
        gaze_coords = self.track_gaze()
        self.show_current_picture(gaze_coords)
        self.root.after(40, self.update_gaze)  # Update every 40 milliseconds


    def show_current_picture(self, gaze_coords):
        if self.image_list:
            self.canvas.delete("all")
            current_image = ImageTk.PhotoImage(self.image_list[self.current_image_idx])
            self.canvas.create_image(0, 0, anchor=tk.NW, image=current_image)
            self.canvas.image = current_image

            # Get gaze coordinates
            self.track_gaze()

            if self.gaze_coords:
                gaze_x, gaze_y = self.gaze_coords
                self.canvas.create_oval(
                    gaze_x - 15, gaze_y - 15, gaze_x + 15, gaze_y + 15,
                    outline="purple", width=2
                )

    def show_previous_picture(self):
        if self.current_image_idx > 0:
            self.current_image_idx -= 1
            self.show_current_picture()
            self.update_button_states()

    def show_next_picture(self):
        if self.current_image_idx < len(self.image_list) - 1:
            self.current_image_idx += 1
            self.show_current_picture(self.gaze_coords)
            self.update_button_states()

    def update_button_states(self):

        if self.current_image_idx > 0:
            self.prev_button["state"] = "normal"
        else:
            self.prev_button["state"] = "disabled"

        if self.current_image_idx < len(self.image_list) - 1:
            self.next_button["state"] = "normal"
        else:
            self.next_button["state"] = "disabled"

    def track_gaze(self):
        _, original_frame = self.webcam.read()
        frame = cv2.flip(original_frame, 1)
        self.gaze.refresh(frame)

        if self.image_list and 0 <= self.current_image_idx < len(self.image_list):
            gaze_horizontal_ratio = self.gaze.horizontal_ratio()
            gaze_vertical_ratio = self.gaze.vertical_ratio()

            if gaze_horizontal_ratio is not None and gaze_vertical_ratio is not None:
                image_width = self.image_list[self.current_image_idx].width
                image_height = self.image_list[self.current_image_idx].height

                # Calculate the gaze point coordinates as the average of left and right eyes
                horizontal_ratio = self.gaze.horizontal_ratio()
                vertical_ratio = self.gaze.vertical_ratio()

                # Calculate the gaze point coordinates as the average of left and right pupils
                gaze_x = int(horizontal_ratio * image_width)
                gaze_y = int(vertical_ratio * image_height)

                self.gaze_coords = (gaze_x, gaze_y)  # Set the gaze coordinates

        return self.gaze_coords  # Return the gaze coordinates

def main():
    root = tk.Tk()
    app = PictureViewer(root)
    root.mainloop()

if __name__ == "__main__":
    main()