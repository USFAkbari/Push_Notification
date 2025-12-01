import FingerprintJS from '@fingerprintjs/fingerprintjs';

let fpPromise = null;
let cachedFingerprint = null;

/**
 * Initialize FingerprintJS
 */
function initFingerprint() {
  if (!fpPromise) {
    fpPromise = FingerprintJS.load();
  }
  return fpPromise;
}

/**
 * Get or generate fingerprint
 */
export async function getFingerprint() {
  // Check cache first
  if (cachedFingerprint) {
    return cachedFingerprint;
  }

  // Check localStorage
  const stored = localStorage.getItem('device_fingerprint');
  if (stored) {
    cachedFingerprint = stored;
    return stored;
  }

  try {
    // Initialize and get fingerprint
    const fp = await initFingerprint();
    const result = await fp.get();
    const fingerprint = result.visitorId;
    
    // Cache it
    cachedFingerprint = fingerprint;
    localStorage.setItem('device_fingerprint', fingerprint);
    
    // Get device info
    const deviceInfo = {
      browser: {
        name: result.components.browserName?.value || 'Unknown',
        version: result.components.browserVersion?.value || 'Unknown'
      },
      os: {
        name: result.components.os?.value || 'Unknown',
        version: result.components.osVersion?.value || 'Unknown'
      },
      device: {
        type: result.components.deviceType?.value || 'Unknown'
      }
    };
    
    return {
      fingerprint,
      deviceInfo
    };
  } catch (error) {
    console.error('Error generating fingerprint:', error);
    // Fallback to a simple fingerprint
    const fallback = `fp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    cachedFingerprint = fallback;
    localStorage.setItem('device_fingerprint', fallback);
    return {
      fingerprint: fallback,
      deviceInfo: null
    };
  }
}

/**
 * Get device info only
 */
export async function getDeviceInfo() {
  try {
    const fp = await initFingerprint();
    const result = await fp.get();
    
    return {
      browser: {
        name: result.components.browserName?.value || 'Unknown',
        version: result.components.browserVersion?.value || 'Unknown'
      },
      os: {
        name: result.components.os?.value || 'Unknown',
        version: result.components.osVersion?.value || 'Unknown'
      },
      device: {
        type: result.components.deviceType?.value || 'Unknown'
      }
    };
  } catch (error) {
    console.error('Error getting device info:', error);
    return null;
  }
}

