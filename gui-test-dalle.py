import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
from openai import OpenAI
import webbrowser
import os

# Initialize the client variable
client = None

def get_api_key():
    try:
        with open('OPENAI_API_KEY.txt', 'r') as file:
            api_key = file.read().strip()
            if not api_key:
                raise ValueError("The API key file is empty.")
            return api_key
    except FileNotFoundError:
        raise ValueError("The API key file 'OPENAI_API_KEY.txt' was not found in the current directory. Please create it and put your OpenAI API key in it.")
    except Exception as e:
        raise ValueError(f"An error occurred while reading the API key: {e}")

# Initialize a variable to keep track of the total cost
total_cost = 0.0

def generate_image():
    global total_cost
    
    prompt_text = prompt_textbox.get("1.0", tk.END).strip()
    n_images = int(n_entry.get())
    image_size = size_entry.get()
    image_quality = quality_var.get()
    image_style = style_var.get()
    
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt_text,
            n=n_images,
            size=image_size,
            quality=image_quality,
            style=image_style
        )
        image_url = response.data[0].url
        result_label.config(text="Click here to open the image")
        result_label.bind("<Button-1>", lambda e: webbrowser.open_new(image_url))
        
        # Calculate the cost of the current request
        cost_per_image = calculate_cost(image_size, image_quality)
        current_cost = cost_per_image * n_images
        total_cost += current_cost
        cost_label.config(text=f"Total cost: ${total_cost:.2f}")
    
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def calculate_cost(size, quality):
    if size == "1024x1024":
        return 0.04 if quality == "standard" else 0.08
    elif size in ["1024x1792", "1792x1024"]:
        return 0.08 if quality == "standard" else 0.12
    else:
        return 0  # Default to 0 for any unexpected size

def show_pricing():
    pricing_info = (
        "Standard\t1024×1024\t$0.040 / image\n"
        "Standard\t1024×1792, 1792×1024\t$0.080 / image\n"
        "HD\t1024×1024\t$0.080 / image\n"
        "HD\t1024×1792, 1792×1024\t$0.120 / image"
    )
    messagebox.showinfo("Pricing Information", pricing_info)

def undo(event):
    try:
        prompt_textbox.edit_undo()
    except tk.TclError:
        pass

def redo(event):
    try:
        prompt_textbox.edit_redo()
    except tk.TclError:
        pass


# Check for OpenAI API key text file in current directory
try:
    api_key = get_api_key()
    client = OpenAI(api_key=api_key)
except ValueError as e:
    messagebox.showerror("API Key Error", e)
    exit()  # Exit the program if the API key is not found or is invalid


if __name__ == "__main__":
    # Initialize the Tkinter window
    window = tk.Tk()
    window.title("DALL-E 3 Image Generator GUI")

    # Create and place UI elements
    prompt_label = tk.Label(window, text="Prompt:")
    prompt_label.pack()
    prompt_textbox = scrolledtext.ScrolledText(window, height=4, width=50, undo=True)
    prompt_textbox.pack()
    prompt_textbox.bind('<Control-z>', undo)
    prompt_textbox.bind('<Control-y>', redo)

    n_label = tk.Label(window, text="Number of images (n):")
    n_label.pack()
    n_entry = tk.Entry(window, width=5)
    n_entry.pack()
    n_entry.insert(0, "1")  # Default value

    size_label = tk.Label(window, text="Size (e.g., 1024x1024):")
    size_label.pack()
    size_entry = tk.Entry(window, width=10)
    size_entry.pack()
    size_entry.insert(0, "1024x1024")  # Default value

    quality_label = tk.Label(window, text="Quality (standard or hd):")
    quality_label.pack()
    quality_var = tk.StringVar(value="standard")  # Default value
    quality_options = ttk.Combobox(window, textvariable=quality_var, values=["standard", "hd"])
    quality_options.pack()

    style_label = tk.Label(window, text="Style (vivid or natural):")
    style_label.pack()
    style_var = tk.StringVar(value="vivid")  # Default value
    style_options = ttk.Combobox(window, textvariable=style_var, values=["vivid", "natural"])
    style_options.pack()

    # Place the 'Pricing' button
    pricing_button = tk.Button(window, text="Pricing", command=show_pricing)
    pricing_button.pack()

    # Place the cost label
    cost_label = tk.Label(window, text=f"Total cost this session: ${total_cost:.2f}")
    cost_label.pack()

    generate_button = tk.Button(window, text="Generate Image", command=generate_image)
    generate_button.pack()

    result_label = tk.Label(window, text="Generated image URL will appear here", fg="blue", cursor="hand2")
    result_label.pack()

    # Start the GUI loop
    window.mainloop()
