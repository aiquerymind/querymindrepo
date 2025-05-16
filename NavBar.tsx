import React from 'react';
import { useNavigate } from '@remix-run/react';

const Navbar: React.FC = () => {
  const navigate = useNavigate();

  return (
    <nav style={styles.nav}>
      <div style={styles.logo}>QueryMind AI</div>
      <div style={styles.navActions}>
        <button style={styles.tipsButton}>
          <span style={styles.starIcon}>✨</span> New! Founders Tips
        </button>
        <button style={styles.signInButton} onClick={() => navigate('/login')}>
          Sign In
        </button>
        <button style={styles.getStartedButton} onClick={() => navigate('/signup')}>
          Get Started
        </button>
      </div>
    </nav>
  );
};

const styles: { [key: string]: React.CSSProperties } = {
  nav: {
    position: 'absolute',
    top: 0,
    left: 0,
    width: '100%',
    padding: '10px 20px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    background: 'transparent',
    zIndex: 20,
  },
  logo: {
    fontSize: '24px',
    fontWeight: 700,
    color: '#1488FC',
  },
  navActions: {
    display: 'flex',
    gap: '10px',
    alignItems: 'center',
  },
  tipsButton: {
    display: 'flex',
    alignItems: 'center',
    background: 'rgba(51, 51, 51, 0.8)',
    color: '#A3A3A3',
    border: 'none',
    borderRadius: '20px',
    padding: '8px 16px',
    fontSize: '14px',
    cursor: 'pointer',
  },
  starIcon: {
    marginRight: '5px',
  },
  signInButton: {
    background: 'transparent',
    color: '#A3A3A3',
    border: 'none',
    fontSize: '14px',
    cursor: 'pointer',
  },
  getStartedButton: {
    background: '#1488FC',
    color: 'white',
    border: 'none',
    borderRadius: '20px',
    padding: '8px 16px',
    fontSize: '14px',
    cursor: 'pointer',
  },
};

export default Navbar;