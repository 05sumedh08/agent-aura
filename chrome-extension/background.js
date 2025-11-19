// Agent Aura Chrome Extension - Background Service Worker
// Handles background tasks, notifications, and data synchronization

// Extension installation
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === 'install') {
    console.log('Agent Aura extension installed');
    
    // Set default configuration
    chrome.storage.sync.set({
      apiUrl: 'http://localhost:8000',
      apiKey: '',
      autoSync: false,
      syncInterval: 60, // minutes
      notifications: true
    });
    
    // Open welcome page
    chrome.tabs.create({
      url: 'http://localhost:3000/admin/agent'
    });
  } else if (details.reason === 'update') {
    console.log('Agent Aura extension updated');
  }
});

// Message handling
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'openPopup') {
    chrome.action.openPopup();
  }
  else if (request.action === 'notify') {
    showNotification(request.title, request.message, request.type);
  }
  else if (request.action === 'syncData') {
    syncDataInBackground(request.data).then(sendResponse);
    return true; // Async response
  }
  
  return true;
});

// Show browser notification
function showNotification(title, message, type = 'info') {
  chrome.storage.sync.get(['notifications'], (config) => {
    if (!config.notifications) return;
    
    const iconMap = {
      success: 'icons/icon-success.png',
      error: 'icons/icon-error.png',
      warning: 'icons/icon-warning.png',
      info: 'icons/icon48.png'
    };
    
    chrome.notifications.create({
      type: 'basic',
      iconUrl: iconMap[type] || iconMap.info,
      title: title,
      message: message,
      priority: type === 'error' ? 2 : 1
    });
  });
}

// Background data synchronization
async function syncDataInBackground(data) {
  try {
    const config = await chrome.storage.sync.get(['apiUrl', 'apiKey']);
    const apiUrl = config.apiUrl || 'http://localhost:8000';
    
    const response = await fetch(`${apiUrl}/api/v1/sync`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': config.apiKey ? `Bearer ${config.apiKey}` : ''
      },
      body: JSON.stringify(data)
    });
    
    if (response.ok) {
      const result = await response.json();
      showNotification(
        'Sync Complete',
        `Successfully synced ${result.count} records`,
        'success'
      );
      return { success: true, result };
    } else {
      throw new Error('Sync failed');
    }
  } catch (error) {
    console.error('Sync error:', error);
    showNotification(
      'Sync Failed',
      'Could not sync data with Agent Aura',
      'error'
    );
    return { success: false, error: error.message };
  }
}

// Auto-sync scheduler
let syncInterval = null;

async function startAutoSync() {
  const config = await chrome.storage.sync.get(['autoSync', 'syncInterval']);
  
  if (!config.autoSync) {
    stopAutoSync();
    return;
  }
  
  const intervalMs = (config.syncInterval || 60) * 60 * 1000; // Convert to ms
  
  syncInterval = setInterval(async () => {
    console.log('Running auto-sync...');
    
    // Get all open tabs with school management systems
    const tabs = await chrome.tabs.query({
      url: [
        '*://*.schoology.com/*',
        '*://*.canvas.instructure.com/*',
        '*://*.blackboard.com/*',
        '*://*.moodle.com/*',
        '*://*.powerschool.com/*',
        '*://*.schoolmanager.com/*'
      ]
    });
    
    if (tabs.length === 0) {
      console.log('No school system tabs open for auto-sync');
      return;
    }
    
    // Sync data from first matching tab
    try {
      const response = await chrome.tabs.sendMessage(tabs[0].id, {
        action: 'syncAllData'
      });
      
      if (response && response.success) {
        console.log(`Auto-sync completed: ${response.count} records`);
      }
    } catch (error) {
      console.error('Auto-sync error:', error);
    }
  }, intervalMs);
  
  console.log(`Auto-sync started: every ${config.syncInterval} minutes`);
}

function stopAutoSync() {
  if (syncInterval) {
    clearInterval(syncInterval);
    syncInterval = null;
    console.log('Auto-sync stopped');
  }
}

// Listen for configuration changes
chrome.storage.onChanged.addListener((changes, namespace) => {
  if (namespace === 'sync') {
    if (changes.autoSync || changes.syncInterval) {
      startAutoSync();
    }
  }
});

// Context menu integration
chrome.runtime.onInstalled.addListener(() => {
  // Add context menu items
  chrome.contextMenus.create({
    id: 'agent-aura-analyze',
    title: 'Analyze with Agent Aura',
    contexts: ['selection']
  });
  
  chrome.contextMenus.create({
    id: 'agent-aura-scan',
    title: 'Scan page for students',
    contexts: ['page']
  });
});

// Handle context menu clicks
chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (info.menuItemId === 'agent-aura-analyze') {
    // Analyze selected text
    const config = await chrome.storage.sync.get(['apiUrl', 'apiKey']);
    
    try {
      const response = await fetch(`${config.apiUrl}/api/v1/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': config.apiKey ? `Bearer ${config.apiKey}` : ''
        },
        body: JSON.stringify({
          text: info.selectionText
        })
      });
      
      if (response.ok) {
        showNotification(
          'Analysis Started',
          'Agent Aura is analyzing the selected text',
          'success'
        );
      }
    } catch (error) {
      showNotification(
        'Analysis Failed',
        'Could not start analysis',
        'error'
      );
    }
  }
  else if (info.menuItemId === 'agent-aura-scan') {
    // Scan page
    try {
      const response = await chrome.tabs.sendMessage(tab.id, {
        action: 'scanStudents'
      });
      
      if (response && response.success) {
        showNotification(
          'Scan Complete',
          `Found ${response.count} students on this page`,
          'success'
        );
      }
    } catch (error) {
      showNotification(
        'Scan Failed',
        'Could not scan this page',
        'error'
      );
    }
  }
});

// Initialize auto-sync on startup
startAutoSync();

console.log('Agent Aura background service worker initialized');
