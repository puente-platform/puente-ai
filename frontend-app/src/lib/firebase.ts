import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider, OAuthProvider } from "firebase/auth";
import { getAnalytics } from "firebase/analytics";

const firebaseConfig = {
  apiKey: "AIzaSyDz4rbfSyDsrPxR4ySD3-KXxAKl-2rCGlo",
  authDomain: "puente-ai-dev.firebaseapp.com",
  projectId: "puente-ai-dev",
  storageBucket: "puente-ai-dev.firebasestorage.app",
  messagingSenderId: "519686233522",
  appId: "1:519686233522:web:757b8eafabd3e2be3d18ab",
  measurementId: "G-WJHJK79MDN",
};

const app = initializeApp(firebaseConfig);

export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider();
export const appleProvider = new OAuthProvider("apple.com");

// Analytics — only initialize in browser
export const analytics = typeof window !== "undefined" ? getAnalytics(app) : null;
