// import { useEffect } from "react";
// import { useNavigate } from "react-router-dom";
// import { useAuth } from "../context/AuthContext";

// const Chat = () => {
//   const { login } = useAuth();
//   const navigate = useNavigate();

//   useEffect(() => {
//     const params = new URLSearchParams(window.location.search);
//     const token = params.get("token");

//     if (token) {
//       login({ token });
//       navigate("/chat"); // optional: remove query params
//     }
//   }, [login, navigate]);

//   return <div>Welcome to Chat!</div>;
// };

// export default Chat;







import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Loader2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const OAuthCallback = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { login } = useAuth();
  const [error, setError] = useState(null);

  useEffect(() => {
    const handleOAuthCallback = () => {
      try {
        console.log('🔍 OAuth Callback - Current URL:', window.location.href);
        console.log('🔍 All params:', Object.fromEntries(searchParams));

        // Get parameters from URL
        const token = searchParams.get('token');
        const email = searchParams.get('email');
        const id = searchParams.get('id');

        console.log('📝 Extracted params:', { 
          token: token ? `${token.substring(0, 20)}...` : 'missing', 
          email, 
          id 
        });

        if (token && email && id) {
          // Store user data
          const userData = {
            id: parseInt(id),
            email: email,
            name: email.split('@')[0]
          };

          console.log('💾 Saving user data:', userData);

          // Store in localStorage
          localStorage.setItem('user', JSON.stringify(userData));
          localStorage.setItem('token', token);

          // Update auth context
          login(userData);

          console.log('✅ Login successful, redirecting to /chat');

          // Navigate to chat
          navigate('/chat', { replace: true });
        } else {
          console.error('❌ Missing OAuth parameters:', { token: !!token, email, id });
          setError('Missing authentication parameters');
          setTimeout(() => {
            navigate('/auth', { replace: true });
          }, 2000);
        }
      } catch (error) {
        console.error('❌ OAuth callback error:', error);
        setError(error.message || 'Authentication failed');
        setTimeout(() => {
          navigate('/auth', { replace: true });
        }, 2000);
      }
    };

    // Small delay to ensure URL params are available
    const timer = setTimeout(handleOAuthCallback, 100);
    return () => clearTimeout(timer);
  }, [navigate, searchParams, login]);

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-100">
        <div className="bg-white p-8 rounded-lg shadow-md max-w-md">
          <div className="text-red-500 text-xl mb-4">❌ Authentication Error</div>
          <p className="text-gray-700 mb-4">{error}</p>
          <p className="text-sm text-gray-500">Redirecting to login...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-md">
        <div className="flex flex-col items-center">
          <Loader2 className="w-12 h-12 animate-spin text-blue-500 mb-4" />
          <p className="text-gray-700">Completing sign in...</p>
          <p className="text-sm text-gray-500 mt-2">Please wait...</p>
        </div>
      </div>
    </div>
  );
};

export default OAuthCallback;