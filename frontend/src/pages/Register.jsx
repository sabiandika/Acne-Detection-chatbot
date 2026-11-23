
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Eye, EyeOff, Sparkles } from 'lucide-react';
import '../styles/auth.css';

function Register() {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const navigate = useNavigate();

  const handleRegister = (e) => {
    e.preventDefault();

    const form = e.currentTarget;

    if (form.password.value !== form.confirmPassword.value) {
      alert('Password dan konfirmasi password tidak sama!');
      return;
    }

    alert('Pendaftaran berhasil! Ini masih simulasi FrontEnd.');
    navigate('/login');
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
            Every skin has its own story.
            Start your journey with us.
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
            <span className="eyebrow">JOIN OUR COMMUNITY</span>
            <h2>Create Account</h2>
            <p>
              Create your account and discover your skin's needs.
            </p>
          </div>

          <form onSubmit={handleRegister}>
            <div className="form-group">
              <label>Full Name</label>
              <input
                type="text"
                name="fullName"
                placeholder="Enter your full name"
                required
              />
            </div>

            <div className="form-group">
              <label>Email Address</label>
              <input
                type="email"
                name="email"
                placeholder="Enter your email"
                required
              />
            </div>

            <div className="form-group">
              <label>Password</label>

              <div className="password-wrapper">
                <input
                  type={showPassword ? 'text' : 'password'}
                  name="password"
                  placeholder="Create a password"
                  minLength="6"
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

            <div className="form-group">
              <label>Confirm Password</label>

              <div className="password-wrapper">
                <input
                  type={showConfirm ? 'text' : 'password'}
                  name="confirmPassword"
                  placeholder="Confirm your password"
                  required
                />

                <button
                  type="button"
                  className="password-toggle"
                  onClick={() => setShowConfirm(!showConfirm)}
                >
                  {showConfirm ? <EyeOff size={19} /> : <Eye size={19} />}
                </button>
              </div>
            </div>

            <button type="submit" className="auth-button">
              Create Account
            </button>
          </form>

          <div className="auth-switch">
            Already have an account?
            <Link to="/login"> Sign In</Link>
          </div>

          <div className="auth-footer">
            © 2026 Rijema Dira. All rights reserved.
          </div>
        </div>
      </div>
    </div>
  );
}

export default Register;
