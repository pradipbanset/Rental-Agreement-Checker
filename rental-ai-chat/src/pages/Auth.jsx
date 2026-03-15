import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Mail, Smartphone, Chrome, Apple, AppWindow } from "lucide-react";

const Auth = () => {
  const [email, setEmail] = useState("");
  const { login } = useAuth();
  const navigate = useNavigate();

  // Email login
  const continueWithEmail = async () => {
    if (!email) return alert("Enter your email");
    try {
      const response = await fetch("http://127.0.0.1:8000/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });
      if (!response.ok) throw new Error("Login failed");
      const data = await response.json();
      login(data);
      navigate("/chat");
    } catch (err) {
      console.error(err);
      alert("Login failed: " + err.message);
    }
  };

  // OAuth login (redirect to backend)
  const handleProviderLogin = (provider) => {
    window.location.href = `http://127.0.0.1:8000/api/login/${provider.toLowerCase()}`;
  };

  return (
    <div className="min-h-screen bg-white flex items-center justify-center px-4">
      <div className="w-full max-w-md border rounded-2xl p-8 shadow-sm">
        <h1 className="text-2xl font-semibold mb-2">Log in or sign up</h1>
        <p className="text-gray-600 mb-6 text-sm">
          You’ll get smarter responses and can upload files, images, and more.
        </p>

        {/* Social logins */}
        <div className="space-y-3">
          <button
            onClick={() => handleProviderLogin("google")}
            className="w-full flex items-center justify-center gap-3 border rounded-lg py-3 hover:bg-gray-50"
          >
            <Chrome className="w-5 h-5" />
            Continue with Google
          </button>

          <button
            onClick={() => handleProviderLogin("apple")}
            className="w-full flex items-center justify-center gap-3 border rounded-lg py-3 hover:bg-gray-50"
          >
            <Apple className="w-5 h-5" />
            Continue with Apple
          </button>

          <button
            onClick={() => handleProviderLogin("microsoft")}
            className="w-full flex items-center justify-center gap-3 border rounded-lg py-3 hover:bg-gray-50"
          >
            <AppWindow className="w-5 h-5" />
            Continue with Microsoft
          </button>

          <button
            onClick={() => handleProviderLogin("phone")}
            className="w-full flex items-center justify-center gap-3 border rounded-lg py-3 hover:bg-gray-50"
          >
            <Smartphone className="w-5 h-5" />
            Continue with phone
          </button>
        </div>

        {/* Divider */}
        <div className="flex items-center gap-3 my-6">
          <div className="flex-1 h-px bg-gray-200" />
          <span className="text-xs text-gray-400">OR</span>
          <div className="flex-1 h-px bg-gray-200" />
        </div>

        {/* Email login */}
        <div className="space-y-3">
          <div className="relative">
            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="email"
              placeholder="Email address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full pl-10 pr-4 py-3 border rounded-lg focus:outline-none"
            />
          </div>

          <button
            onClick={continueWithEmail}
            className="w-full bg-black text-white py-3 rounded-lg font-medium"
          >
            Continue
          </button>
        </div>

        <p className="text-xs text-gray-400 text-center mt-6">
          No password required • Just a magic link sent to your email.
        </p>
      </div>
    </div>
  );
};

export default Auth;
