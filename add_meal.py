import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import csv
import json
import os
import datetime
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# File paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, "meal_log.csv")
WEIGHT_FILE = os.path.join(BASE_DIR, "weight_log.csv")
DB_FILE = os.path.join(BASE_DIR, "food_db.json")
SETTINGS_FILE = os.path.join(BASE_DIR, "user_settings.json")

DEFAULT_DB = {
    "morning": {
        "protein_powder": {"serving": 100, "kcal": 370.0, "protein": 29.0, "carbs": 50.0, "fat": 8.24},
        "banana": {"serving": 1, "kcal": 89.0, "protein": 1.1, "carbs": 23.0, "fat": 0.3},
        "channa": {"serving": 50, "kcal": 180.0, "protein": 9, "carbs": 30.0, "fat": 3},
        "chia seeds": {"serving": 100, "kcal": 490.0, "protein": 16, "carbs": 44.0, "fat": 31},
        "sunflower seeds": {"serving": 100, "kcal": 582.0, "protein": 19, "carbs": 24.0, "fat": 55},
        "flax seeds": {"serving": 100, "kcal": 534.0, "protein": 18, "carbs": 29.0, "fat": 42},
        "pumpkin seeds": {"serving": 100, "kcal": 446.0, "protein": 19, "carbs": 54.0, "fat": 19},
        "dabur_honey": {"serving": 100, "kcal": 320.0, "protein": 0, "carbs": 80.0, "fat": 0},
    },
    "lunch": {
        "oats Yogabar": {"serving": 50, "kcal": 177.0, "protein": 13, "carbs": 26, "fat": 3.6},
        "oats pintola": {"serving": 50, "kcal": 196.0, "protein": 12.5, "carbs": 27.3, "fat": 3.9},
        "oats MB": {"serving": 100, "kcal": 386.0, "protein": 12, "carbs": 68, "fat": 9.5},
        "milk": {"serving": 100, "kcal": 87.0, "protein": 3.2, "carbs": 5.0, "fat": 6.0},
        "milk low fat": {"serving": 100, "kcal": 47.0, "protein": 3.3, "carbs": 5.0, "fat": 1.5},
        "peanut_butter": {"serving": 32, "kcal": 192.0, "protein": 9.6, "carbs": 5.4, "fat": 14.7},
        "sattu": {"serving": 50, "kcal": 205.5, "protein": 11.0, "carbs": 23.0, "fat": 6.0},
    },
    "evening": {
        "egg": {"serving": 1, "kcal": 78.0, "protein": 5.5, "carbs": 0.4, "fat": 5.3},
    },
    "dinner": {
        "roti": {"serving": 1, "kcal": 90.0, "protein": 2.5, "carbs": 16.5, "fat": 1.5},
        "rice": {"serving": 100, "kcal": 130.0, "protein": 2.5, "carbs": 28.0, "fat": 0.3},
        "paneer bhurji": {"serving": 250, "kcal": 290.0, "protein": 15, "carbs": 20.0, "fat": 20},
    }
}

DEFAULT_SETTINGS = {
    "goal_kcal": 2500,
    "goal_protein": 120,
    "bulk_mode": False,
    "theme": "Dark"
}

class NutriFitApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("NutriFit Pro 🚀")
        self.geometry("900x700")

        self.db = self.load_json(DB_FILE, DEFAULT_DB)
        self.settings = self.load_json(SETTINGS_FILE, DEFAULT_SETTINGS)

        ctk.set_appearance_mode(self.settings["theme"])
        ctk.set_default_color_theme("green")

        self.ensure_csvs()

        # Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(6, weight=1)

        ctk.CTkLabel(self.sidebar, text="NutriFit Pro 💪", font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, padx=20, pady=(20, 30))

        self.btn_dash = ctk.CTkButton(self.sidebar, text="Dashboard 📊", command=lambda: self.select_frame("dash"))
        self.btn_dash.grid(row=1, column=0, padx=20, pady=10)

        self.btn_log = ctk.CTkButton(self.sidebar, text="Log Meal 🥗", command=lambda: self.select_frame("log"))
        self.btn_log.grid(row=2, column=0, padx=20, pady=10)

        self.btn_food = ctk.CTkButton(self.sidebar, text="Add Foods 🥑", command=lambda: self.select_frame("food"))
        self.btn_food.grid(row=3, column=0, padx=20, pady=10)

        self.btn_weight = ctk.CTkButton(self.sidebar, text="Weight & Trends 📈", command=lambda: self.select_frame("weight"))
        self.btn_weight.grid(row=4, column=0, padx=20, pady=10)

        self.btn_settings = ctk.CTkButton(self.sidebar, text="Settings ⚙️", command=lambda: self.select_frame("settings"))
        self.btn_settings.grid(row=5, column=0, padx=20, pady=10)

        self.bulk_switch = ctk.CTkSwitch(self.sidebar, text="BULK MODE 🔥", command=self.toggle_bulk, onvalue=1, offvalue=0)
        self.bulk_switch.grid(row=7, column=0, padx=20, pady=20)
        if self.settings.get("bulk_mode"):
            self.bulk_switch.select()
        else:
            self.bulk_switch.deselect()

        # Main Frame containers
        self.frames = {}
        for F in ["dash", "log", "food", "weight", "settings"]:
            frame = ctk.CTkFrame(self, corner_radius=10)
            self.frames[F] = frame

        # Init frames
        self.init_dashboard()
        self.init_log_meal()
        self.init_add_food()
        self.init_weight_trends()
        self.init_settings()

        self.select_frame("dash")

    # --- Utility Methods ---
    def load_json(self, path, default):
        if not os.path.exists(path):
            with open(path, 'w') as f:
                json.dump(default, f, indent=4)
            return default
        with open(path, 'r') as f:
            try:
                return json.load(f)
            except:
                return default

    def save_json(self, path, data):
        with open(path, 'w') as f:
            json.dump(data, f, indent=4)

    def ensure_csvs(self):
        if not os.path.exists(CSV_FILE):
            pd.DataFrame(columns=["Date", "Meal", "Calories", "Protein", "Carbs", "Fat"]).to_csv(CSV_FILE, index=False)
        if not os.path.exists(WEIGHT_FILE):
            pd.DataFrame(columns=["Date", "Weight"]).to_csv(WEIGHT_FILE, index=False)

    def get_goals(self):
        k = self.settings["goal_kcal"]
        p = self.settings["goal_protein"]
        if self.settings.get("bulk_mode"):
            return k * 1.2, p * 1.2
        return k, p

    def toggle_bulk(self):
        self.settings["bulk_mode"] = self.bulk_switch.get() == 1
        self.save_settings()
        self.refresh_dashboard()
        
        mode = "ON 🔥! Targets increased by +20%" if self.settings["bulk_mode"] else "OFF. Targets normal."
        messagebox.showinfo("Bulk Mode", f"Bulk Mode turned {mode}")

    def save_settings(self):
        self.save_json(SETTINGS_FILE, self.settings)

    def select_frame(self, name):
        for f in self.frames.values():
            f.grid_forget()
        self.frames[name].grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        if name == "dash":
            self.refresh_dashboard()
        elif name == "weight":
            self.refresh_trends()
        elif name == "log":
            self.refresh_log_meal_auto_select()

    # --- Dashboard UI ---
    def init_dashboard(self):
        f = self.frames["dash"]
        f.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(f, text="Today's Overview", font=ctk.CTkFont(size=28, weight="bold")).pack(pady=20)

        self.dash_stats = ctk.CTkFrame(f, fg_color="transparent")
        self.dash_stats.pack(fill="x", padx=20)

        self.cal_lbl = ctk.CTkLabel(self.dash_stats, text="🔥 Calories: 0 / 2500", font=ctk.CTkFont(size=18))
        self.cal_lbl.pack(anchor="w", pady=5)
        self.cal_bar = ctk.CTkProgressBar(self.dash_stats, width=600, height=20, corner_radius=10, progress_color="#FF5722")
        self.cal_bar.pack(anchor="w", pady=(0, 20))

        self.pro_lbl = ctk.CTkLabel(self.dash_stats, text="💪 Protein: 0 / 120", font=ctk.CTkFont(size=18))
        self.pro_lbl.pack(anchor="w", pady=5)
        self.pro_bar = ctk.CTkProgressBar(self.dash_stats, width=600, height=20, corner_radius=10, progress_color="#388E3C")
        self.pro_bar.pack(anchor="w", pady=(0, 20))

        self.warning_lbl = ctk.CTkLabel(f, text="", font=ctk.CTkFont(size=16, weight="bold"), text_color="orange")
        self.warning_lbl.pack(pady=30)

        actions = ctk.CTkFrame(f, fg_color="transparent")
        actions.pack(pady=20)
        
        ctk.CTkButton(actions, text="Delete Last Logged Meal 🗑️", fg_color="#D32F2F", hover_color="#B71C1C", 
                      command=self.delete_last_meal).pack(side="left", padx=10)

    def get_today_totals(self):
        today = datetime.date.today().isoformat()
        try:
            df = pd.read_csv(CSV_FILE)
            df_today = df[df['Date'] == today]
            if df_today.empty:
                return 0, 0
            return df_today['Calories'].sum(), df_today['Protein'].sum()
        except:
            return 0, 0

    def refresh_dashboard(self):
        cal, pro = self.get_today_totals()
        goal_c, goal_p = self.get_goals()

        cal_pct = min(cal/goal_c, 1.0) if goal_c > 0 else 0
        pro_pct = min(pro/goal_p, 1.0) if goal_p > 0 else 0

        self.cal_lbl.configure(text=f"🔥 Calories: {cal:.0f} / {goal_c:.0f} kcal ({cal_pct*100:.0f}%)")
        self.cal_bar.set(cal_pct)

        self.pro_lbl.configure(text=f"💪 Protein: {pro:.0f} / {goal_p:.0f} g ({pro_pct*100:.0f}%)")
        self.pro_bar.set(pro_pct)

        rem_p = goal_p - pro
        if rem_p > 0:
            best_foods = self.get_high_protein_foods()
            sugg = f"⚠️ You need {rem_p:.0f}g more protein today!\n\n💡 Try adding: {', '.join(best_foods[:3])}"
            self.warning_lbl.configure(text=sugg, text_color="orange")
        else:
            self.warning_lbl.configure(text="✅ Protein goal reached! Great job! 💪", text_color="#388E3C")

    def get_high_protein_foods(self):
        # find items with high protein per serving
        items = []
        for m, foods in self.db.items():
            for name, info in foods.items():
                if info["serving"] > 0 and info["protein"] > 5:
                     items.append((name.replace('_', ' ').title(), info["protein"]/info["serving"]))
        items.sort(key=lambda x: x[1], reverse=True)
        return [x[0] for x in items]

    def delete_last_meal(self):
        try:
            df = pd.read_csv(CSV_FILE)
            if df.empty:
                messagebox.showinfo("Info", "No meals to delete.")
                return
            last = df.iloc[-1]
            df = df.iloc[:-1]
            df.to_csv(CSV_FILE, index=False)
            messagebox.showinfo("Deleted", f"Deleted last log: {last['Meal']} ({last['Calories']} kcal)")
            self.refresh_dashboard()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete meal: {e}")

    # --- Log Meal UI ---
    def init_log_meal(self):
        f = self.frames["log"]
        ctk.CTkLabel(f, text="Log a Meal 🥗", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)

        self.meal_type_var = tk.StringVar(value="morning")
        self.meal_combo = ctk.CTkOptionMenu(f, variable=self.meal_type_var, values=["morning", "lunch", "evening", "dinner"], command=self.load_meal_form)
        self.meal_combo.pack(pady=10)

        self.meal_form_frame = ctk.CTkScrollableFrame(f, width=500, height=400)
        self.meal_form_frame.pack(pady=10, fill="both", expand=True)

        self.meal_entries = {}
        
        ctk.CTkButton(f, text="Save Meal ✅", command=self.save_meal_log).pack(pady=20)

    def refresh_log_meal_auto_select(self):
        hour = datetime.datetime.now().hour
        if hour < 12: meal = "morning"
        elif hour < 17: meal = "lunch"
        elif hour < 20: meal = "evening"
        else: meal = "dinner"
        self.meal_type_var.set(meal)
        self.load_meal_form(meal)

    def load_meal_form(self, meal_type):
        for widget in self.meal_form_frame.winfo_children():
            widget.destroy()
        
        self.meal_entries.clear()
        foods = self.db.get(meal_type, {})
        if not foods:
            ctk.CTkLabel(self.meal_form_frame, text="No foods in this category yet. Add some!").pack(pady=20)
            return

        for idx, (item, info) in enumerate(foods.items()):
            row = ctk.CTkFrame(self.meal_form_frame, fg_color="transparent")
            row.pack(fill="x", pady=5)
            
            srv = info["serving"]
            label_text = f"{item.replace('_', ' ').title()} (per {srv} {'unit' if srv==1 else 'g/ml'}):"
            ctk.CTkLabel(row, text=label_text, width=250, anchor="w").pack(side="left")
            
            ent = ctk.CTkEntry(row, placeholder_text="Qty", width=80)
            ent.pack(side="right")
            self.meal_entries[item] = ent

    def save_meal_log(self):
        meal = self.meal_type_var.get()
        totals = {"kcal":0, "protein":0, "carbs":0, "fat":0}
        
        for item, ent in self.meal_entries.items():
            val = ent.get()
            if val:
                try:
                    qty = float(val)
                    if qty < 0: raise ValueError
                    info = self.db[meal][item]
                    factor = qty / info["serving"]
                    totals["kcal"] += info["kcal"] * factor
                    totals["protein"] += info["protein"] * factor
                    totals["carbs"] += info["carbs"] * factor
                    totals["fat"] += info["fat"] * factor
                except ValueError:
                    messagebox.showerror("Error", f"Invalid quantity for {item}")
                    return

        if sum(totals.values()) == 0:
            messagebox.showinfo("Info", "No quantities entered. Skipping.")
            return

        date_iso = datetime.date.today().isoformat()
        try:
            df = pd.read_csv(CSV_FILE)
            new_row = pd.DataFrame([{
                "Date": date_iso, 
                "Meal": meal, 
                "Calories": round(totals["kcal"],1),
                "Protein": round(totals["protein"],1),
                "Carbs": round(totals["carbs"],1),
                "Fat": round(totals["fat"],1)
            }])
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv(CSV_FILE, index=False)

            messagebox.showinfo("Success", f"Logged {meal.title()} 🥗\n\n🔥 Calories: {totals['kcal']:.0f} kcal\n💪 Protein: {totals['protein']:.0f}g")
            self.select_frame("dash")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save meal: {e}")

    # --- Add Food UI ---
    def init_add_food(self):
        f = self.frames["food"]
        ctk.CTkLabel(f, text="Add Custom Food 🥑", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)
        
        form = ctk.CTkFrame(f, width=400)
        form.pack(pady=10, padx=50, fill="y")
        
        ctk.CTkLabel(form, text="Meal Category:").pack(pady=(10,0))
        self.nc_meal = ctk.CTkOptionMenu(form, values=["morning", "lunch", "evening", "dinner"])
        self.nc_meal.pack(pady=5)
        
        ctk.CTkLabel(form, text="Food Name:").pack(pady=(10,0))
        self.nc_name = ctk.CTkEntry(form, width=200)
        self.nc_name.pack(pady=5)
        
        ctk.CTkLabel(form, text="Serving Size (g/ml/units):").pack(pady=(10,0))
        self.nc_serving = ctk.CTkEntry(form, width=200)
        self.nc_serving.pack(pady=5)
        
        ctk.CTkLabel(form, text="Calories (kcal):").pack(pady=(10,0))
        self.nc_kcal = ctk.CTkEntry(form, width=200)
        self.nc_kcal.pack(pady=5)
        
        ctk.CTkLabel(form, text="Protein (g):").pack(pady=(10,0))
        self.nc_protein = ctk.CTkEntry(form, width=200)
        self.nc_protein.pack(pady=5)
        
        ctk.CTkLabel(form, text="Carbs (g):").pack(pady=(10,0))
        self.nc_carbs = ctk.CTkEntry(form, width=200)
        self.nc_carbs.pack(pady=5)
        
        ctk.CTkLabel(form, text="Fat (g):").pack(pady=(10,0))
        self.nc_fat = ctk.CTkEntry(form, width=200)
        self.nc_fat.pack(pady=5)
        
        ctk.CTkButton(form, text="Add to Database 💾", command=self.save_custom_food).pack(pady=20)

    def save_custom_food(self):
        meal = self.nc_meal.get()
        name = self.nc_name.get().strip().lower()
        try:
            srv = float(self.nc_serving.get())
            kcal = float(self.nc_kcal.get())
            pro = float(self.nc_protein.get())
            carbs = float(self.nc_carbs.get())
            fat = float(self.nc_fat.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for nutrients.")
            return

        if not name:
            messagebox.showerror("Error", "Food name cannot be empty.")
            return

        self.db[meal][name] = {
            "serving": srv, "kcal": kcal, "protein": pro, "carbs": carbs, "fat": fat
        }
        self.save_json(DB_FILE, self.db)
        messagebox.showinfo("Success", f"Successfully added {name.title()} to {meal} meals!")
        
        # Clear fields
        self.nc_name.delete(0, 'end')
        self.nc_serving.delete(0, 'end')
        self.nc_kcal.delete(0, 'end')
        self.nc_protein.delete(0, 'end')
        self.nc_carbs.delete(0, 'end')
        self.nc_fat.delete(0, 'end')

    # --- Weight & Trends UI ---
    def init_weight_trends(self):
        self.wt_frame = self.frames["weight"]
        ctk.CTkLabel(self.wt_frame, text="Weight Tracking & Trends 📈", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=10)
        
        inp_frame = ctk.CTkFrame(self.wt_frame, fg_color="transparent")
        inp_frame.pack(pady=10)
        
        ctk.CTkLabel(inp_frame, text="Log Today's Weight (kg):", font=ctk.CTkFont(size=14)).pack(side="left", padx=10)
        self.wt_entry = ctk.CTkEntry(inp_frame, width=80)
        self.wt_entry.pack(side="left", padx=10)
        ctk.CTkButton(inp_frame, text="Log Weight", width=100, command=self.save_weight).pack(side="left")

        self.graph_frame = ctk.CTkFrame(self.wt_frame)
        self.graph_frame.pack(fill="both", expand=True, padx=20, pady=10)

    def save_weight(self):
        val = self.wt_entry.get()
        try:
            weight = float(val)
        except ValueError:
            messagebox.showerror("Error", "Invalid weight.")
            return
            
        date_iso = datetime.date.today().isoformat()
        try:
            df = pd.read_csv(WEIGHT_FILE)
            if date_iso in df['Date'].values:
                df.loc[df['Date'] == date_iso, 'Weight'] = weight
            else:
                new_row = pd.DataFrame([{"Date": date_iso, "Weight": weight}])
                df = pd.concat([df, new_row], ignore_index=True)
                
            df.to_csv(WEIGHT_FILE, index=False)
            self.wt_entry.delete(0, 'end')
            messagebox.showinfo("Saved", f"Weight successfully logged: {weight} kg")
            self.refresh_trends()
        except:
            messagebox.showerror("Error", "Could not save weight log.")

    def refresh_trends(self):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

        plt.close('all') # Prevent memory leaks
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6, 5))
        fig.tight_layout(pad=4.0)
        
        # Colors for themes
        bg_col = "#2b2b2b" if self.settings["theme"] == "Dark" else "#ebebeb"
        fg_col = "white" if self.settings["theme"] == "Dark" else "black"
        fig.patch.set_facecolor(bg_col)
        
        for ax in (ax1, ax2):
            ax.set_facecolor(bg_col)
            ax.tick_params(colors=fg_col)
            ax.xaxis.label.set_color(fg_col)
            ax.yaxis.label.set_color(fg_col)
            ax.title.set_color(fg_col)
            for spine in ax.spines.values():
                spine.set_edgecolor(fg_col)

        # Plot 1: Calories & Protein Last 7 Days
        try:
            df_meals = pd.read_csv(CSV_FILE)
            if not df_meals.empty:
                df_meals['Date'] = pd.to_datetime(df_meals['Date'])
                last7 = df_meals[df_meals['Date'] >= (pd.Timestamp.now() - pd.Timedelta(days=7))]
                daily = last7.groupby('Date')[['Calories', 'Protein']].sum().reset_index()
                
                # Check if group wasn't empty
                if not daily.empty:
                    daily['DateStr'] = daily['Date'].dt.strftime('%m-%d')
                    
                    ax1.plot(daily['DateStr'], daily['Calories'], marker='o', color='orange', label='Calories')
                    ax1.set_title("Last 7 Days Output")
                    ax1.grid(True, alpha=0.3)
                    ax1.set_ylabel("Calories", color='orange')
                    ax1.tick_params(axis='y', colors='orange')
                    
                    ax1_b = ax1.twinx()
                    ax1_b.plot(daily['DateStr'], daily['Protein'], marker='s', color='#388E3C', label='Protein')
                    ax1_b.set_ylabel("Protein (g)", color='#388E3C')
                    ax1_b.tick_params(axis='y', colors='#388E3C')
                    
                    # Weekly Averages Text
                    avg_c = daily['Calories'].mean()
                    avg_p = daily['Protein'].mean()
                    fig.text(0.5, 0.50, f"Weekly Average: 🔥 {avg_c:.0f} kcal / 💪 {avg_p:.0f} g", 
                             ha='center', color=fg_col, weight='bold', fontsize=10)
        except:
            pass

        # Plot 2: Weight Progress
        try:
            df_wt = pd.read_csv(WEIGHT_FILE)
            if not df_wt.empty:
                df_wt['Date'] = pd.to_datetime(df_wt['Date'])
                df_wt = df_wt.sort_values('Date')
                df_wt['DateStr'] = df_wt['Date'].dt.strftime('%m-%d')
                ax2.plot(df_wt['DateStr'], df_wt['Weight'], marker='D', color='dodgerblue', linewidth=2)
                ax2.set_title("Weight Progression Tracker")
                ax2.set_ylabel("Weight (kg)")
                ax2.grid(True, alpha=0.3)
        except:
            pass

        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    # --- Settings UI ---
    def init_settings(self):
        f = self.frames["settings"]
        ctk.CTkLabel(f, text="Settings ⚙️", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)
        
        form = ctk.CTkFrame(f, width=400)
        form.pack(pady=10, padx=50, fill="y")
        
        ctk.CTkLabel(form, text="Base Daily Calorie Goal (kcal):").pack(pady=(10,0))
        self.set_kcal = ctk.CTkEntry(form)
        self.set_kcal.pack(pady=5)
        self.set_kcal.insert(0, str(self.settings["goal_kcal"]))
        
        ctk.CTkLabel(form, text="Base Daily Protein Goal (g):").pack(pady=(10,0))
        self.set_pro = ctk.CTkEntry(form)
        self.set_pro.pack(pady=5)
        self.set_pro.insert(0, str(self.settings["goal_protein"]))
        
        ctk.CTkLabel(form, text="Theme (Dark/Light/System):").pack(pady=(10,0))
        self.set_theme = ctk.CTkOptionMenu(form, values=["Dark", "Light", "System"])
        self.set_theme.pack(pady=5)
        self.set_theme.set(self.settings.get("theme", "Dark"))
        
        ctk.CTkButton(form, text="Save Settings 💾", command=self.save_settings_ui).pack(pady=20)

    def save_settings_ui(self):
        try:
            self.settings["goal_kcal"] = float(self.set_kcal.get())
            self.settings["goal_protein"] = float(self.set_pro.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid goal values.")
            return
            
        theme = self.set_theme.get()
        self.settings["theme"] = theme
        ctk.set_appearance_mode(theme)
        
        self.save_settings()
        messagebox.showinfo("Saved", "Settings updated successfully!")
        self.refresh_dashboard()

if __name__ == "__main__":
    app = NutriFitApp()
    app.mainloop()