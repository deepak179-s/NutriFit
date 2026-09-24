# NutriFit Pro 🥗

NutriFit Pro is a modern, sleek, and feature-rich nutrition and health tracking web application. Designed with an elegant glassmorphism aesthetic, it offers users a premium tracking experience across both desktop and mobile devices.

## ✨ Features

- **NutriFit AI Coach (Powered by Gemini)**: A smart, conversational AI nutritionist. Ask for meal ideas, track your macros, or simply upload a photo of your food for the AI to instantly analyze and auto-log to your daily diary!
- **Gemini-Inspired Chat Interface**: Features a beautiful, responsive chat UI with multi-session chat history, image upload capabilities, and a sleek mobile drawer layout.
- **Dynamic Dashboard**: Track your daily calories, protein, carbs, and fat with visual progress rings and an interactive meal breakdown.
- **Glassmorphism UI**: A stunning frosted-glass aesthetic combined with smooth micro-animations, light/dark modes, and a vibrant animated mesh background.
- **Water Tracking**: Easily record your daily water intake towards an 8-glass daily goal directly from the dashboard.
- **Trends & Charts**: Visualizes your weight and calorie intake over the last 14 days using built-in HTML5 Canvas charts.
- **Custom Food Database**: Log common meals or save custom entries for rapid logging in the future.
- **Cloud Sync**: Securely store and sync your meal logs, weight data, and chat sessions across devices using Firebase Firestore.

## 🛠️ Technologies Used

- **Vite**: Next-generation frontend tooling for ultra-fast builds.
- **Vanilla JavaScript, HTML5, CSS3**: Lightweight frontend without heavy framework dependencies for maximum performance.
- **Google Gemini API**: Advanced multimodal AI for the NutriFit Coach and food image analysis.
- **Firebase Firestore**: Real-time cloud database integration and user authentication.
- **Vercel**: Seamless continuous deployment and hosting.

## 🚀 Installation & Usage

1. **Clone the repository:**
   ```bash
   git clone https://github.com/deepak179-s/NutriFit.git
   cd NutriFit
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure Environment Variables:**
   Create a `.env` file in the root directory and add your API keys:
   ```env
   VITE_FIREBASE_API_KEY="your-firebase-api-key"
   VITE_FIREBASE_AUTH_DOMAIN="your-firebase-project.firebaseapp.com"
   VITE_FIREBASE_PROJECT_ID="your-project-id"
   VITE_FIREBASE_STORAGE_BUCKET="your-project-id.appspot.com"
   VITE_FIREBASE_MESSAGING_SENDER_ID="your-sender-id"
   VITE_FIREBASE_APP_ID="your-app-id"
   VITE_GEMINI_API_KEY="your-gemini-api-key"
   ```

4. **Start the development server:**
   ```bash
   npm run dev
   ```

5. **Build for production:**
   ```bash
   npm run build
   ```

## ☁️ Deployment

NutriFit Pro is configured for seamless deployment on **Vercel**. 
1. Connect your GitHub repository to Vercel.
2. Ensure the Framework Preset is set to **Vite**.
3. Add the environment variables (`VITE_FIREBASE_...` and `VITE_GEMINI_API_KEY`) in the Vercel dashboard.
4. Deploy!

## 📄 License
ISC
