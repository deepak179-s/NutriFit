# NutriFit Pro

NutriFit Pro is a modern, sleek, and feature-rich nutrition and health tracking desktop application built with Electron. It leverages an elegant glassmorphism aesthetic, offering users a premium tracking experience right from their desktop.

## Features

- **Dashboard**: Track your daily calories, protein, carbs, and fat with visual progress rings and an interactive meal breakdown.
- **Glassmorphism UI**: A stunning frosted-glass aesthetic combined with smooth micro-animations and a vibrant gradient background.
- **Water Tracking**: Easily record your daily water intake towards an 8-glass daily goal directly from the dashboard.
- **Trends & Charts**: Visualizes your weight and calorie intake over the last 14 days using built-in HTML5 Canvas charts.
- **Custom Food Database**: Log common meals or save custom entries for rapid logging in the future.
- **Cloud Sync**: Securely store and sync your meal logs, weight data, and database across devices using Firebase Firestore.

## Technologies Used

- **Electron**: Cross-platform desktop application framework.
- **Vanilla JavaScript, HTML5, CSS3**: Lightweight frontend without heavy framework dependencies.
- **Firebase Firestore**: Real-time cloud database integration.

## Installation & Usage

1. **Clone the repository:**
   ```bash
   git clone https://github.com/deepak179-s/NutriFit.git
   cd NutriFit
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the application:**
   ```bash
   npm start
   ```

4. **Build for production:**
   ```bash
   npm run build
   ```

## Developer Notes

This app relies on Firebase for cloud synchronization. Ensure you have the proper Firebase credentials set up in `index.html` if you plan to fork and host your own database instance.

## License
ISC
