import React, { useState, useEffect } from 'react';
import { FaPhoneAlt, FaShieldAlt, FaAmbulance, FaFireExtinguisher } from 'react-icons/fa';

function EmergencyButton() {
  const [showEmergency, setShowEmergency] = useState(false);
  const [countdown, setCountdown] = useState(5);
  const [emergencyType, setEmergencyType] = useState('police');
  const [isCalling, setIsCalling] = useState(false);

  // Emergency numbers
  const emergencyNumbers = {
    police: '100',
    ambulance: '108',
    fire: '101',
    women: '1091'  // Women's helpline
  };

  // Handle hardware button simulation (for web, we use keyboard)
  useEffect(() => {
    const handleKeyPress = (e) => {
      // Simulate volume button press (Volume Up = F2, Volume Down = F1)
      if (e.key === 'F2' || e.key === 'F1' || e.key === 'Escape') {
        e.preventDefault();
        triggerEmergency();
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, []);

  // Countdown timer
  useEffect(() => {
    let timer;
    if (showEmergency && countdown > 0) {
      timer = setTimeout(() => {
        setCountdown(countdown - 1);
      }, 1000);
    } else if (showEmergency && countdown === 0) {
      makeEmergencyCall();
    }
    return () => clearTimeout(timer);
  }, [showEmergency, countdown]);

  const triggerEmergency = () => {
    setShowEmergency(true);
    setCountdown(5);
  };

  const cancelEmergency = () => {
    setShowEmergency(false);
    setCountdown(5);
    setIsCalling(false);
  };

  const makeEmergencyCall = () => {
    setIsCalling(true);
    const number = emergencyNumbers[emergencyType];
    
    // For web demo, show alert
    alert(`🔴 EMERGENCY CALL INITIATED\nCalling ${emergencyType.toUpperCase()} at ${number}`);
    
    // In a real mobile app, this would trigger the phone dialer
    window.location.href = `tel:${number}`;
    
    // Reset after 3 seconds
    setTimeout(() => {
      setShowEmergency(false);
      setIsCalling(false);
      setCountdown(5);
    }, 3000);
  };

  if (!showEmergency) {
    return (
      <div className="emergency-floating-button" onClick={triggerEmergency}>
        <FaPhoneAlt className="emergency-icon" />
        <span className="emergency-text">SOS</span>
        <div className="pulse-ring"></div>
      </div>
    );
  }

  return (
    <div className="emergency-modal">
      <div className="emergency-content">
        <div className="emergency-header">
          <FaShieldAlt className="emergency-logo" />
          <h2>🚨 EMERGENCY SOS 🚨</h2>
        </div>

        <div className="emergency-timer">
          <div className="timer-circle">
            <span className="timer-number">{countdown}</span>
            <span className="timer-label">seconds</span>
          </div>
          <p className="timer-text">Calling in {countdown}s...</p>
        </div>

        <div className="emergency-options">
          <button 
            className={`emergency-option ${emergencyType === 'police' ? 'active' : ''}`}
            onClick={() => setEmergencyType('police')}
          >
            <FaShieldAlt /> Police
            <span className="number">{emergencyNumbers.police}</span>
          </button>
          <button 
            className={`emergency-option ${emergencyType === 'ambulance' ? 'active' : ''}`}
            onClick={() => setEmergencyType('ambulance')}
          >
            <FaAmbulance /> Ambulance
            <span className="number">{emergencyNumbers.ambulance}</span>
          </button>
          <button 
            className={`emergency-option ${emergencyType === 'fire' ? 'active' : ''}`}
            onClick={() => setEmergencyType('fire')}
          >
            <FaFireExtinguisher /> Fire
            <span className="number">{emergencyNumbers.fire}</span>
          </button>
          <button 
            className={`emergency-option ${emergencyType === 'women' ? 'active' : ''}`}
            onClick={() => setEmergencyType('women')}
          >
            👩 Women Helpline
            <span className="number">{emergencyNumbers.women}</span>
          </button>
        </div>

        <div className="emergency-actions">
          <button className="call-now-btn" onClick={makeEmergencyCall}>
            📞 CALL NOW
          </button>
          <button className="cancel-btn" onClick={cancelEmergency}>
            ✕ CANCEL
          </button>
        </div>

        <p className="emergency-note">
          ⚠️ Emergency call will be made to {emergencyType.toUpperCase()} at {emergencyNumbers[emergencyType]}
        </p>
      </div>
    </div>
  );
}

export default EmergencyButton;