# gui.py
import tkinter as tk
from tkinter import ttk, messagebox
from recommender import load_data, compute_similarity, get_recommendations_by_title
import pandas as pd

# Load data and compute similarity
user_ratings, merged = load_data('./data/credits.csv', './data/titles.csv')
movie_similarity, movie_indices = compute_similarity(user_ratings)

# Function to update the autocomplete list
def update_autocomplete(*args):
    search_term = title_entry.get().strip().lower()
    if search_term:
        matches = user_ratings[user_ratings['title'].str.contains(search_term, case=False, na=False)]
        unique_titles = matches['title'].unique().tolist()
        listbox_update(unique_titles)
    else:
        listbox_clear()

# Function to update the Listbox
def listbox_update(data):
    listbox.delete(0, tk.END)
    for item in data:
        listbox.insert(tk.END, item)
    listbox.place(x=title_entry.winfo_x(), y=title_entry.winfo_y() + title_entry.winfo_height())

# Function to clear the Listbox
def listbox_clear():
    listbox.delete(0, tk.END)
    listbox.place_forget()

# Function to select an item from the Listbox
def on_listbox_select(event):
    selection = listbox.get(listbox.curselection())
    title_entry.delete(0, tk.END)
    title_entry.insert(0, selection)
    listbox_clear()

# Function to show recommendations
def show_recommendations():
    title = title_entry.get().strip()
    if not title:
        messagebox.showerror("Error", "Please select a movie title")
        return
    
    matches = user_ratings[user_ratings['title'] == title]
    
    if matches.empty:
        messagebox.showerror("Error", "No movies found with that title")
        return

    matches = pd.merge(matches, merged[['title', 'release_year']], on='title', how='left')
    matches = matches.rename(columns={'release_year': 'year'})

    unique_matches = matches.drop_duplicates(subset=['title', 'year'])

    if len(unique_matches) > 1:
        dropdown_menu['values'] = [f"{row['title']} ({row['year']})" for _, row in unique_matches.iterrows()]
        dropdown_menu.current(0)
    recommendations = get_recommendations_by_title(unique_matches.iloc[0]['title'], movie_similarity, movie_indices)
    if recommendations:
        recommendations_text.set("\n".join(recommendations))

# Create the main window
root = tk.Tk()
root.title("Movie Recommender System")
root.geometry("600x400")

# Movie title label and entry
tk.Label(root, text="Search Movie Title:").grid(row=0, column=0, padx=10, pady=10)
title_entry = tk.Entry(root, width=50)
title_entry.grid(row=0, column=1, padx=10, pady=10)
title_entry.bind("<KeyRelease>", update_autocomplete)

# Listbox for autocomplete suggestions
listbox = tk.Listbox(root, width=50)
listbox.bind("<<ListboxSelect>>", on_listbox_select)

# Show recommendations button
recommend_button = tk.Button(root, text="Show Recommendations", command=show_recommendations)
recommend_button.grid(row=1, columnspan=2, pady=10)

# Recommendations text
recommendations_text = tk.StringVar()
tk.Label(root, textvariable=recommendations_text, wraplength=500, justify="left").grid(row=3, columnspan=2, padx=10, pady=10)

# Run the application
root.mainloop()
