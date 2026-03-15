const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api";

/**
 * Login with email
 */
export const loginWithEmail = async (email) => {
  const response = await fetch(`${API_URL}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(error || "Login failed");
  }

  return response.json(); // Expect { email, name, token }
};

/**
 * Login with OAuth/social provider
 */
export const loginWithProvider = async (provider) => {
  const response = await fetch(`${API_URL}/login/${provider}`, {
    method: "POST",
  });

  if (!response.ok) throw new Error(`${provider} login failed`);

  return response.json(); // Expect { email, name, token }
};
