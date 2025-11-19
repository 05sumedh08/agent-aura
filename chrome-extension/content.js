// Agent Aura Chrome Extension - Content Script
// Runs on school management system pages to extract student data

// Supported school management systems
const SYSTEMS = {
  SCHOOLOGY: 'schoology.com',
  CANVAS: 'canvas.instructure.com',
  BLACKBOARD: 'blackboard.com',
  MOODLE: 'moodle.com',
  POWERSCHOOL: 'powerschool.com',
  SCHOOLMANAGER: 'schoolmanager.com'
};

// Detect current system
function detectSystem() {
  const url = window.location.hostname;
  
  for (const [name, domain] of Object.entries(SYSTEMS)) {
    if (url.includes(domain)) {
      return name;
    }
  }
  
  return null;
}

// Data extractors for different systems
const Extractors = {
  // Schoology extractor
  SCHOOLOGY: {
    scanStudents() {
      const students = [];
      
      // Try to find student rows in gradebook
      const rows = document.querySelectorAll('.gradebook-row, .student-row, tr[data-student-id]');
      
      rows.forEach(row => {
        const nameEl = row.querySelector('.student-name, .name-column, td[data-student-name]');
        const idEl = row.getAttribute('data-student-id') || row.querySelector('[data-student-id]')?.getAttribute('data-student-id');
        const gradeEl = row.querySelector('.grade, .current-grade, td[data-grade]');
        
        if (nameEl && idEl) {
          students.push({
            id: idEl,
            name: nameEl.textContent.trim(),
            grade: gradeEl?.textContent.trim() || 'N/A',
            system: 'Schoology'
          });
        }
      });
      
      return students;
    },
    
    getStudentData() {
      // Extract data from student profile page
      const nameEl = document.querySelector('.student-profile-name, h1.student-name');
      const idEl = document.querySelector('[data-student-id]');
      
      if (!nameEl) return null;
      
      return {
        studentId: idEl?.getAttribute('data-student-id') || 'unknown',
        studentName: nameEl.textContent.trim(),
        system: 'Schoology'
      };
    }
  },
  
  // Canvas LMS extractor
  CANVAS: {
    scanStudents() {
      const students = [];
      const rows = document.querySelectorAll('.student_row, .student, tr.student_assignment');
      
      rows.forEach(row => {
        const nameEl = row.querySelector('.student-name a, .user_name a');
        const idAttr = row.id || row.getAttribute('data-user-id');
        const id = idAttr?.replace('student_', '').replace('user_', '');
        
        if (nameEl && id) {
          students.push({
            id: id,
            name: nameEl.textContent.trim(),
            system: 'Canvas'
          });
        }
      });
      
      return students;
    },
    
    getStudentData() {
      const nameEl = document.querySelector('.student_context_card_name, h2.student-name');
      const idEl = document.querySelector('[data-student-id]');
      
      if (!nameEl) return null;
      
      return {
        studentId: idEl?.getAttribute('data-student-id') || window.location.pathname.split('/').pop(),
        studentName: nameEl.textContent.trim(),
        system: 'Canvas'
      };
    }
  },
  
  // Generic extractor (fallback)
  GENERIC: {
    scanStudents() {
      const students = [];
      
      // Look for common patterns
      const possibleRows = document.querySelectorAll('tr, .student, .row, [class*="student"]');
      
      possibleRows.forEach(row => {
        // Look for name-like text
        const text = row.textContent;
        if (text.match(/[A-Z][a-z]+\s+[A-Z][a-z]+/)) {
          // Possible student name found
          const match = text.match(/([A-Z][a-z]+\s+[A-Z][a-z]+)/);
          if (match) {
            students.push({
              id: `generic_${students.length}`,
              name: match[1],
              system: 'Generic'
            });
          }
        }
      });
      
      return students;
    },
    
    getStudentData() {
      // Try to find any name-like text
      const heading = document.querySelector('h1, h2, .student-name, .name');
      if (!heading) return null;
      
      return {
        studentId: 'unknown',
        studentName: heading.textContent.trim(),
        system: 'Generic'
      };
    }
  }
};

// Add Agent Aura button to page
function addAgentAuraButton() {
  // Check if button already exists
  if (document.getElementById('agent-aura-btn')) return;
  
  const button = document.createElement('button');
  button.id = 'agent-aura-btn';
  button.className = 'agent-aura-floating-btn';
  button.innerHTML = '🤖';
  button.title = 'Open Agent Aura';
  
  button.addEventListener('click', () => {
    chrome.runtime.sendMessage({ action: 'openPopup' });
  });
  
  document.body.appendChild(button);
}

// Extract student data based on current system
function extractStudents() {
  const system = detectSystem();
  const extractor = Extractors[system] || Extractors.GENERIC;
  
  return extractor.scanStudents();
}

// Get single student data
function getStudentData() {
  const system = detectSystem();
  const extractor = Extractors[system] || Extractors.GENERIC;
  
  return extractor.getStudentData();
}

// Sync all data with Agent Aura
async function syncAllData() {
  const students = extractStudents();
  
  if (students.length === 0) {
    return { success: false, message: 'No students found' };
  }
  
  // Get API configuration
  const config = await chrome.storage.sync.get(['apiUrl', 'apiKey']);
  const apiUrl = config.apiUrl || 'http://localhost:8000';
  
  try {
    // Send students to API
    const response = await fetch(`${apiUrl}/api/v1/students/bulk`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': config.apiKey ? `Bearer ${config.apiKey}` : ''
      },
      body: JSON.stringify({ students })
    });
    
    if (response.ok) {
      return { success: true, count: students.length };
    } else {
      return { success: false, message: 'API request failed' };
    }
  } catch (error) {
    console.error('Sync error:', error);
    return { success: false, message: error.message };
  }
}

// Message listener from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'scanStudents') {
    const students = extractStudents();
    sendResponse({ success: true, count: students.length, students });
  }
  else if (request.action === 'getStudentData') {
    const data = getStudentData();
    if (data) {
      sendResponse({ success: true, ...data });
    } else {
      sendResponse({ success: false });
    }
  }
  else if (request.action === 'syncAllData') {
    syncAllData().then(result => sendResponse(result));
    return true; // Async response
  }
  
  return true;
});

// Initialize
function init() {
  console.log('Agent Aura extension loaded');
  
  // Add floating button
  addAgentAuraButton();
  
  // Detect system
  const system = detectSystem();
  if (system) {
    console.log(`Detected system: ${system}`);
  }
}

// Run initialization when page loads
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
