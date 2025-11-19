// Agent Aura Chrome Extension - Popup Script
// Handles UI interactions and configuration

// Configuration management
const Config = {
  async get(key) {
    const result = await chrome.storage.sync.get(key);
    return result[key];
  },
  
  async set(key, value) {
    await chrome.storage.sync.set({ [key]: value });
  },
  
  async getAll() {
    const data = await chrome.storage.sync.get(['apiUrl', 'apiKey', 'lastSync']);
    return {
      apiUrl: data.apiUrl || 'http://localhost:8000',
      apiKey: data.apiKey || '',
      lastSync: data.lastSync || null
    };
  }
};

// Message display utility
function showMessage(text, type = 'success') {
  const messageEl = document.getElementById('message');
  messageEl.textContent = text;
  messageEl.className = `message ${type} show`;
  
  setTimeout(() => {
    messageEl.classList.remove('show');
  }, 3000);
}

// Loading state
function setLoading(isLoading) {
  const loadingEl = document.getElementById('loading');
  const container = document.querySelector('.container');
  
  if (isLoading) {
    loadingEl.classList.add('show');
    container.style.opacity = '0.5';
  } else {
    loadingEl.classList.remove('show');
    container.style.opacity = '1';
  }
}

// Initialize popup
async function init() {
  // Load saved configuration
  const config = await Config.getAll();
  document.getElementById('api-url').value = config.apiUrl;
  document.getElementById('api-key').value = config.apiKey;
  
  // Check connection status
  await checkConnection(config.apiUrl);
  
  // Detect current page
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  detectPage(tab.url);
}

// Check API connection
async function checkConnection(apiUrl) {
  const statusEl = document.getElementById('connection-status');
  const dotEl = document.querySelector('.dot');
  
  try {
    const response = await fetch(`${apiUrl}/api/health`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    });
    
    if (response.ok) {
      statusEl.textContent = 'Connected';
      dotEl.style.background = '#4ade80';
    } else {
      statusEl.textContent = 'Error';
      dotEl.style.background = '#fbbf24';
    }
  } catch (error) {
    statusEl.textContent = 'Offline';
    dotEl.style.background = '#ef4444';
  }
}

// Detect current school management system
function detectPage(url) {
  const pageEl = document.getElementById('current-page');
  
  const systems = {
    'schoology.com': 'Schoology',
    'canvas.instructure.com': 'Canvas LMS',
    'blackboard.com': 'Blackboard',
    'moodle.com': 'Moodle',
    'powerschool.com': 'PowerSchool',
    'schoolmanager.com': 'School Manager'
  };
  
  for (const [domain, name] of Object.entries(systems)) {
    if (url.includes(domain)) {
      pageEl.textContent = name;
      return;
    }
  }
  
  pageEl.textContent = 'Not detected';
}

// Save configuration
document.getElementById('save-config').addEventListener('click', async () => {
  const apiUrl = document.getElementById('api-url').value.trim();
  const apiKey = document.getElementById('api-key').value.trim();
  
  if (!apiUrl) {
    showMessage('Please enter an API URL', 'error');
    return;
  }
  
  try {
    await Config.set('apiUrl', apiUrl);
    await Config.set('apiKey', apiKey);
    
    // Test connection
    await checkConnection(apiUrl);
    
    showMessage('Configuration saved successfully', 'success');
  } catch (error) {
    showMessage('Failed to save configuration', 'error');
  }
});

// Scan students on current page
document.getElementById('scan-students').addEventListener('click', async () => {
  setLoading(true);
  
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    // Send message to content script to scan page
    const response = await chrome.tabs.sendMessage(tab.id, {
      action: 'scanStudents'
    });
    
    if (response && response.success) {
      showMessage(`Found ${response.count} students`, 'success');
    } else {
      showMessage('No students found on this page', 'error');
    }
  } catch (error) {
    showMessage('Failed to scan page. Make sure you\'re on a supported page.', 'error');
  } finally {
    setLoading(false);
  }
});

// Analyze risk for current student
document.getElementById('analyze-risk').addEventListener('click', async () => {
  setLoading(true);
  
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    const config = await Config.getAll();
    
    // Send message to content script to get student data
    const response = await chrome.tabs.sendMessage(tab.id, {
      action: 'getStudentData'
    });
    
    if (response && response.success) {
      // Send to Agent Aura API
      const apiResponse = await fetch(`${config.apiUrl}/api/v1/agent/goal`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': config.apiKey ? `Bearer ${config.apiKey}` : ''
        },
        body: JSON.stringify({
          student_id: response.studentId,
          goal: `Analyze risk factors for student: ${response.studentName}`,
          enabled_agents: [true, true, true, true]
        })
      });
      
      if (apiResponse.ok) {
        showMessage('Risk analysis started', 'success');
      } else {
        showMessage('Failed to start analysis', 'error');
      }
    } else {
      showMessage('Could not detect student on this page', 'error');
    }
  } catch (error) {
    showMessage('Analysis failed. Check your configuration.', 'error');
  } finally {
    setLoading(false);
  }
});

// Open Agent Aura dashboard
document.getElementById('open-dashboard').addEventListener('click', async () => {
  const config = await Config.getAll();
  const dashboardUrl = config.apiUrl.replace(':8000', ':3000');
  chrome.tabs.create({ url: `${dashboardUrl}/admin/teachers` });
});

// Sync data with Agent Aura
document.getElementById('sync-data').addEventListener('click', async () => {
  setLoading(true);
  
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    // Send message to content script to extract all data
    const response = await chrome.tabs.sendMessage(tab.id, {
      action: 'syncAllData'
    });
    
    if (response && response.success) {
      await Config.set('lastSync', new Date().toISOString());
      showMessage(`Synced ${response.count} records`, 'success');
    } else {
      showMessage('Sync failed', 'error');
    }
  } catch (error) {
    showMessage('Sync failed. Check your connection.', 'error');
  } finally {
    setLoading(false);
  }
});

// Open Agent Aura app
document.getElementById('open-app').addEventListener('click', async () => {
  const config = await Config.getAll();
  const appUrl = config.apiUrl.replace(':8000', ':3000');
  chrome.tabs.create({ url: appUrl });
});

// View documentation
document.getElementById('view-docs').addEventListener('click', () => {
  chrome.tabs.create({ url: 'https://github.com/05sumedh08/agent-aura/wiki' });
});

// Initialize on load
document.addEventListener('DOMContentLoaded', init);
