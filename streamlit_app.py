import streamlit as st
import pandas as pd
import json
import os
import datetime

# File paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, "meal_log.csv")
WEIGHT_FILE = os.path.join(BASE_DIR, "weight_log.csv")
DB_FILE = os.path.join(BASE_DIR, "food_db.json")
SETTINGS_FILE = os.path.join(BASE_DIR, "user_settings.json")

# Defaults
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
    "bulk_mode": False
}

st.set_page_config(page_title="NutriFit Pro", page_icon="🏋️‍♂️", layout="wide")

st.markdown("""
    <style>
    .big-font {
        font-size:30px !important;
        font-weight: bold;
    }
    .stProgress .st-bo {
        background-color: #4CAF50;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Helper Functions ---
def load_json(path, default):
    if not os.path.exists(path):
        with open(path, 'w') as f:
            json.dump(default, f, indent=4)
        return default
    with open(path, 'r') as f:
        try:
            return json.load(f)
        except:
            return default

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)

def ensure_csvs():
    if not os.path.exists(CSV_FILE):
        pd.DataFrame(columns=["Date", "Meal", "Calories", "Protein", "Carbs", "Fat"]).to_csv(CSV_FILE, index=False)
    if not os.path.exists(WEIGHT_FILE):
        pd.DataFrame(columns=["Date", "Weight"]).to_csv(WEIGHT_FILE, index=False)

ensure_csvs()

if 'db' not in st.session_state:
    st.session_state.db = load_json(DB_FILE, DEFAULT_DB)
if 'settings' not in st.session_state:
    st.session_state.settings = load_json(SETTINGS_FILE, DEFAULT_SETTINGS)

def get_goals():
    k = st.session_state.settings["goal_kcal"]
    p = st.session_state.settings["goal_protein"]
    if st.session_state.settings.get("bulk_mode"):
        return k * 1.2, p * 1.2
    return k, p

# --- Sidebar Navigation ---
st.sidebar.markdown('<p class="big-font">NutriFit Pro 💪</p>', unsafe_allow_html=True)
nav = st.sidebar.radio("Navigation", ["Dashboard 📊", "Log Meal 🥗", "Food Database 🥑", "Weight & Trends 📈", "Settings ⚙️"])

st.sidebar.write("---")
if st.sidebar.checkbox("BULK MODE 🔥 (+20% Goals)", value=st.session_state.settings.get("bulk_mode", False)):
    if not st.session_state.settings.get("bulk_mode"):
        st.session_state.settings["bulk_mode"] = True
        save_json(SETTINGS_FILE, st.session_state.settings)
        st.sidebar.success("Targets Increased by 20%!")
        st.rerun()
else:
    if st.session_state.settings.get("bulk_mode"):
        st.session_state.settings["bulk_mode"] = False
        save_json(SETTINGS_FILE, st.session_state.settings)
        st.rerun()

# --- Pages ---
if nav == "Dashboard 📊":
    st.title("Today's Overview")
    df = pd.read_csv(CSV_FILE)
    today = datetime.date.today().isoformat()
    df_today = df[df['Date'] == today]
    
    cal = df_today['Calories'].sum() if not df_today.empty else 0
    pro = df_today['Protein'].sum() if not df_today.empty else 0
    goal_c, goal_p = get_goals()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("🔥 Calories (kcal)", f"{cal:.0f} / {goal_c:.0f}", f"{cal - goal_c:.0f} kcal", delta_color="inverse")
        st.progress(min(cal/goal_c, 1.0) if goal_c > 0 else 0)
    with col2:
        st.metric("💪 Protein (g)", f"{pro:.0f} / {goal_p:.0f}", f"{pro - goal_p:.0f} g")
        st.progress(min(pro/goal_p, 1.0) if goal_p > 0 else 0)
        
    st.write("---")
    
    if pro < goal_p:
        # find suggestions
        items = []
        for m, foods in st.session_state.db.items():
            for name, info in foods.items():
                if info["serving"] > 0 and info["protein"] > 5:
                     items.append((name.replace('_', ' ').title(), info["protein"]))
        items.sort(key=lambda x: x[1], reverse=True)
        top3 = [x[0] for x in items[:3]]
        
        st.warning(f"⚠️ You need **{goal_p - pro:.0f}g** more protein today! \n\n💡 **Try adding:** {', '.join(top3)}")
    else:
        st.success("✅ Daily Protein Goal Reached! Great job! 💪")
        
    st.subheader("Today's Logged Meals")
    if not df_today.empty:
        st.dataframe(df_today[['Meal', 'Calories', 'Protein', 'Carbs', 'Fat']], use_container_width=True)
        
        st.write("### Delete an Entry")
        colA, colB = st.columns([3, 1])
        with colA:
            # Map index to meal string
            options = {idx: f"{row['Meal']} ({row['Calories']} kcal) - {row['Protein']}g Pro" for idx, row in df_today.iterrows()}
            meal_to_delete = st.selectbox("Select specific meal to delete from today:", options.keys(), format_func=lambda x: options[x])
        with colB:
            st.write("")
            st.write("")
            if st.button("Delete Selected Meal 🗑️", use_container_width=True):
                df = df.drop(meal_to_delete)
                df.to_csv(CSV_FILE, index=False)
                st.rerun()
    else:
        st.info("No meals logged today yet. Head over to the **Log Meal 🥗** tab!")

elif nav == "Log Meal 🥗":
    st.title("Log a Meal 🥗")
    
    hour = datetime.datetime.now().hour
    def_idx = 0
    if hour >= 12 and hour < 17: def_idx = 1
    elif hour >= 17 and hour < 20: def_idx = 2
    elif hour >= 20: def_idx = 3

    meal_type = st.selectbox("Select Meal Time", ["morning", "lunch", "evening", "dinner"], index=def_idx)
    
    foods = st.session_state.db.get(meal_type, {})
    if foods:
        st.write("### Select Food Item")
        # Split into columns for a better form layout
        col1, col2 = st.columns(2)
        with col1:
            food_options = list(foods.keys())
            selected_food = st.selectbox("Food Name", food_options, format_func=lambda x: x.replace('_', ' ').title())
            info = foods[selected_food]
            srv = info["serving"]
            
        with col2:
            qty = st.number_input(f"Quantity consumed (Current default serving: {srv} {'unit' if srv==1 else 'g/ml'})", min_value=0.0, value=float(srv), step=1.0)
            
        st.write("### Nutritional Value for this Selection:")
        factor = qty / srv if srv > 0 else 0
        kcal = info["kcal"] * factor
        protein = info["protein"] * factor
        carbs = info["carbs"] * factor
        fat = info["fat"] * factor
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Calories", f"{kcal:.1f} kcal")
        c2.metric("Protein", f"{protein:.1f} g")
        c3.metric("Carbs", f"{carbs:.1f} g")
        c4.metric("Fat", f"{fat:.1f} g")
        
        if st.button("Log Food ✅", use_container_width=True):
            if qty == 0:
                st.error("Quantity cannot be 0!")
            else:
                df = pd.read_csv(CSV_FILE)
                new_row = pd.DataFrame([{
                    "Date": datetime.date.today().isoformat(),
                    "Meal": f"{meal_type.title()} - {selected_food.replace('_', ' ').title()}",
                    "Calories": round(kcal, 1),
                    "Protein": round(protein, 1),
                    "Carbs": round(carbs, 1),
                    "Fat": round(fat, 1)
                }])
                df = pd.concat([df, new_row], ignore_index=True)
                df.to_csv(CSV_FILE, index=False)
                st.success(f"Successfully logged **{selected_food.replace('_', ' ').title()}**! Check dashboard to see your progress.")
    else:
        st.info(f"No foods in {meal_type} category. Add some in the **Food Database 🥑** tab!")

elif nav == "Food Database 🥑":
    st.title("Custom Food Database 🥑")
    st.write("Add your own custom foods and macros to the app!")
    
    with st.form("custom_food_form"):
        col1, col2 = st.columns(2)
        with col1:
            nc_meal = st.selectbox("Meal Category", ["morning", "lunch", "evening", "dinner"])
            nc_name = st.text_input("Food Name (e.g., Chicken Breast)")
            nc_serving = st.number_input("Serving Size (g/ml/units)", min_value=1.0, value=100.0)
        with col2:
            nc_kcal = st.number_input("Calories (kcal)", min_value=0.0, step=10.0)
            nc_protein = st.number_input("Protein (g)", min_value=0.0, step=1.0)
            nc_carbs = st.number_input("Carbs (g)", min_value=0.0, step=1.0)
            nc_fat = st.number_input("Fat (g)", min_value=0.0, step=1.0)
            
        submitted = st.form_submit_button("Add to Database 💾")
        if submitted:
            if nc_name.strip() == "":
                st.error("Food name cannot be empty.")
            else:
                key_name = nc_name.strip().lower().replace(" ", "_")
                st.session_state.db[nc_meal][key_name] = {
                    "serving": nc_serving,
                    "kcal": nc_kcal,
                    "protein": nc_protein,
                    "carbs": nc_carbs,
                    "fat": nc_fat
                }
                save_json(DB_FILE, st.session_state.db)
                st.success(f"Successfully added {nc_name} to {nc_meal}!")
                st.rerun()
                
    st.write("### Current Database Preview")
    view_cat = st.selectbox("Select category to view", ["morning", "lunch", "evening", "dinner"])
    st.json(st.session_state.db[view_cat])

elif nav == "Weight & Trends 📈":
    st.title("Weight & Trends 📈")
    
    # Weight Logging
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Log Weight")
        with st.form("weight_form"):
            today_wt = st.number_input("Today's Weight (kg)", min_value=10.0, value=60.0, step=0.1)
            if st.form_submit_button("Save Weight"):
                df_wt = pd.read_csv(WEIGHT_FILE)
                date_iso = datetime.date.today().isoformat()
                if date_iso in df_wt['Date'].values:
                    df_wt.loc[df_wt['Date'] == date_iso, 'Weight'] = today_wt
                else:
                    new_row = pd.DataFrame([{"Date": date_iso, "Weight": today_wt}])
                    df_wt = pd.concat([df_wt, new_row], ignore_index=True)
                df_wt.to_csv(WEIGHT_FILE, index=False)
                st.success(f"Weight mapped: {today_wt} kg!")
                
    st.write("---")
                
    # Trends Data
    df_wt = pd.read_csv(WEIGHT_FILE)
    df_meals = pd.read_csv(CSV_FILE)
    
    colA, colB = st.columns(2)
    with colA:
        st.subheader("Weight Tracking Progression")
        if not df_wt.empty:
            df_wt['Date'] = pd.to_datetime(df_wt['Date'])
            df_wt = df_wt.sort_values('Date')
            st.line_chart(data=df_wt.set_index('Date')['Weight'], use_container_width=True)
        else:
            st.info("Log some weight to see your progress chart!")
            
    with colB:
        st.subheader("Last 7 Days Macroutrient Trend")
        if not df_meals.empty:
            df_meals['Date'] = pd.to_datetime(df_meals['Date'])
            last7 = df_meals[df_meals['Date'] >= (pd.Timestamp.now() - pd.Timedelta(days=7))]
            if not last7.empty:
                daily = last7.groupby('Date')[['Calories', 'Protein']].sum()
                st.line_chart(daily, use_container_width=True)
            else:
                st.info("No meals logged in the last 7 days.")
        else:
            st.info("No meals logged in the last 7 days.")

elif nav == "Settings ⚙️":
    st.title("General Settings ⚙️")
    
    with st.form("settings_form"):
        st.write("### Macronutrient Goals")
        new_k = st.number_input("Base Daily Calorie Goal (kcal)", value=int(st.session_state.settings["goal_kcal"]), step=100)
        new_p = st.number_input("Base Daily Protein Goal (g)", value=int(st.session_state.settings["goal_protein"]), step=5)
        
        st.write("---")
        st.write("### Display Settings")
        st.info("Streamlit natively supports Dark/Light mode! Click the three dots (⋮) top-right -> Settings -> Theme to change it globally.")
        
        if st.form_submit_button("Save Custom Goals 💾"):
            st.session_state.settings["goal_kcal"] = new_k
            st.session_state.settings["goal_protein"] = new_p
            save_json(SETTINGS_FILE, st.session_state.settings)
            st.success("Custom goals saved successfully!")
