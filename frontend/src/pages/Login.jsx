
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Eye, EyeOff, Sparkles } from 'lucide-react';
import '../styles/auth.css';

function Login() {
  const [showPassword, setShowPassword] = useState(false);
  const navigate = useNavigate();

  const handleLogin = (e) => {
    e.preventDefault();

    navigate('/dashboard');
  };

  return (
    <div className="auth-page">
      <div className="auth-decoration">
        <div className="brand-content">
          <div className="brand-icon">
            <Sparkles size={30} />
          </div>

          <h1>Rijema Dira</h1>
          <p className="brand-tagline">
            Your Skin, Your Confidence.
          </p>

          <div className="brand-description">
            Discover the beauty of your skin
            with the right care and attention.
          </div>
        </div>

        <div className="decoration-circle circle-one"></div>
        <div className="decoration-circle circle-two"></div>
      </div>

      <div className="auth-form-section">
        <div className="auth-form-container">
          <div className="mobile-brand">
            <Sparkles size={24} />
            <span>Rijema Dira</span>
          </div>

          <div className="auth-heading">
            <span className="eyebrow">WELCOME BACK</span>
            <h2>Welcome Back!</h2>
            <p>
              Sign in to continue your skincare journey.
            </p>
          </div>

          <form onSubmit={handleLogin}>
            <div className="form-group">
              <label>Email Address</label>
              <input
                type="email"
                placeholder="Enter your email"
                required
              />
            </div>

            <div className="form-group">
              <label>Password</label>

              <div className="password-wrapper">
                <input
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Enter your password"
                  required
                />

                <button
                  type="button"
                  className="password-toggle"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? <EyeOff size={19} /> : <Eye size={19} />}
                </button>
              </div>
            </div>

            <div className="form-options">
              <label className="remember-option">
                <input type="checkbox" />
                Remember me
              </label>

              <a href="#forgot">Forgot password?</a>
            </div>

            <button type="submit" className="auth-button">
              Sign In
            </button>
          </form>

          <div className="auth-switch">
            Don't have an account?
            <Link to="/register"> Create Account</Link>
          </div>

          <div className="auth-footer">
            © 2026 Rijema Dira. All rights reserved.
          </div>
        </div>
      </div>
    </div>
  );
}

export default Login;
