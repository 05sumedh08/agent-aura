# Agent Aura Chrome Extension

**AI-Powered Student Analytics Integration for School Management Systems**

Seamlessly integrate Agent Aura's advanced AI analytics into your existing school management platform with this lightweight Chrome extension.

## 🎯 Features

### Real-Time Integration
- **Automatic Detection**: Recognizes major school management systems (Schoology, Canvas, Blackboard, Moodle, PowerSchool)
- **One-Click Analysis**: Analyze student risk directly from your current school platform
- **Data Extraction**: Automatically extract student data from gradebooks and profiles
- **Live Sync**: Keep Agent Aura synchronized with your school system data

### Supported Platforms
✅ Schoology  
✅ Canvas LMS  
✅ Blackboard Learn  
✅ Moodle  
✅ PowerSchool  
✅ Generic (works with most school systems)

### Key Capabilities
- 📊 **Scan Students**: Extract student lists from any page
- ⚠️ **Risk Analysis**: Run AI-powered risk assessment on individual students
- 📈 **Quick Dashboard**: Jump directly to Agent Aura analytics dashboard
- 🔄 **Auto-Sync**: Automatically synchronize data at regular intervals
- 🔔 **Notifications**: Get alerts for high-risk students

## 📦 Installation

### From Source (Development)

1. **Clone or Download**
   ```powershell
   cd S:\Courses\Kaggle\Agent_Aura_GIT\chrome-extension
   ```

2. **Open Chrome Extensions**
   - Navigate to `chrome://extensions/`
   - Enable "Developer mode" (toggle in top right)

3. **Load Extension**
   - Click "Load unpacked"
   - Select the `chrome-extension` folder
   - Extension will appear in your toolbar

### From Chrome Web Store (Coming Soon)
*Agent Aura extension will be available on Chrome Web Store soon*

## ⚙️ Configuration

### First-Time Setup

1. **Click Extension Icon** in Chrome toolbar
2. **Configure API Settings**:
   ```
   API URL: http://localhost:8000  (for local development)
   API URL: https://api.agentagura.com  (for production)
   ```
3. **Add API Key** (optional, for production):
   - Generate API key from Agent Aura dashboard
   - Paste into "API Key" field
4. **Save Configuration**

### Auto-Sync Settings
- Enable auto-sync to automatically synchronize data
- Set sync interval (default: 60 minutes)
- Enable/disable notifications

## 🚀 Usage

### Quick Start

1. **Navigate** to your school management system (e.g., Schoology)
2. **Click the floating 🤖 button** or extension icon
3. **Choose an action**:
   - **Scan Students**: Detect all students on current page
   - **Analyze Risk**: Run AI analysis on current student profile
   - **Open Dashboard**: View full Agent Aura analytics
   - **Sync Data**: Upload data to Agent Aura

### Use Cases

#### Scenario 1: Gradebook Analysis
```
1. Open your gradebook in Schoology/Canvas
2. Click "Scan Students" in extension
3. Extension detects all 30 students
4. Click "Sync Data" to upload to Agent Aura
5. View comprehensive analytics in dashboard
```

#### Scenario 2: Individual Student Risk Assessment
```
1. Open student profile page
2. Click extension icon
3. Click "Analyze Risk"
4. Agent Aura runs 4 AI agents in parallel
5. Receive risk assessment with interventions
```

#### Scenario 3: Continuous Monitoring
```
1. Enable auto-sync in extension settings
2. Continue using your school system normally
3. Extension automatically syncs data every hour
4. Receive notifications for high-risk students
```

## 🔧 Technical Details

### Architecture

```
┌─────────────────────────────────────┐
│  School Management System (Web)     │
├─────────────────────────────────────┤
│  Content Script (content.js)        │
│  - Detects system type              │
│  - Extracts student data            │
│  - Adds floating button UI          │
└──────────────┬──────────────────────┘
               │
               ↓
┌─────────────────────────────────────┐
│  Extension Popup (popup.js)         │
│  - Configuration UI                 │
│  - Quick actions                    │
│  - Status display                   │
└──────────────┬──────────────────────┘
               │
               ↓
┌─────────────────────────────────────┐
│  Background Service (background.js)  │
│  - Auto-sync scheduler              │
│  - Notifications                    │
│  - Context menus                    │
└──────────────┬──────────────────────┘
               │
               ↓
┌─────────────────────────────────────┐
│  Agent Aura Backend API             │
│  - Multi-agent processing           │
│  - Risk analysis                    │
│  - Data storage                     │
└─────────────────────────────────────┘
```

### Data Flow

1. **Content Script** extracts data from school system page
2. **Popup** or **Background** sends data to Agent Aura API
3. **API** processes with multi-agent system
4. **Results** displayed in Agent Aura dashboard
5. **Extension** receives notifications for critical alerts

### Security

- 🔒 **HTTPS Only** in production
- 🔑 **API Key Authentication** for secure access
- 🛡️ **CSP Headers** to prevent XSS attacks
- 🚫 **No Data Storage** in extension (uses API)
- ✅ **Minimal Permissions** (only required sites)

## 🧪 Testing

### Manual Testing

1. **Test on Schoology**:
   ```
   - Visit demo.schoology.com
   - Open gradebook
   - Click "Scan Students"
   - Verify student list extracted
   ```

2. **Test API Connection**:
   ```
   - Click extension icon
   - Check "Connection" status
   - Should show green "Connected" dot
   ```

3. **Test Data Sync**:
   ```
   - Click "Sync Data" button
   - Check console for API requests
   - Verify data appears in dashboard
   ```

## 🐛 Troubleshooting

### Extension Not Loading
- Check Chrome version (minimum: Chrome 88+)
- Verify "Developer mode" is enabled
- Check browser console for errors

### Connection Failed
- Verify Agent Aura backend is running
- Check API URL in configuration
- Ensure no firewall blocking localhost:8000

### No Students Detected
- Verify you're on a supported page (gradebook, roster)
- Try different page within school system
- Check browser console for extraction errors

### Sync Failed
- Verify API key is correct (if using)
- Check network tab for failed requests
- Ensure backend API is accessible

## 📝 Development

### File Structure
```
chrome-extension/
├── manifest.json          # Extension configuration
├── popup.html            # Extension popup UI
├── popup.js              # Popup logic
├── content.js            # Page content script
├── content.css           # Injected styles
├── background.js         # Background service worker
├── icons/                # Extension icons
│   ├── icon16.png
│   ├── icon32.png
│   ├── icon48.png
│   └── icon128.png
└── README.md             # This file
```

### Adding Support for New Systems

1. **Add domain to manifest.json**:
   ```json
   "matches": [
     "*://newsystem.com/*"
   ]
   ```

2. **Create extractor in content.js**:
   ```javascript
   NEWSYSTEM: {
     scanStudents() {
       // Implement student extraction
     },
     getStudentData() {
       // Implement single student data
     }
   }
   ```

3. **Test on target system**

### Building for Production

1. **Update manifest.json**:
   - Change version number
   - Update host_permissions for production domain

2. **Create ZIP package**:
   ```powershell
   Compress-Archive -Path chrome-extension/* -DestinationPath agent-aura-extension-v1.0.0.zip
   ```

3. **Submit to Chrome Web Store**:
   - Visit Chrome Web Store Developer Dashboard
   - Upload ZIP file
   - Fill in store listing details
   - Submit for review

## 🔄 Updates

### Version 1.0.0 (Current)
- ✅ Initial release
- ✅ Support for 6 major school systems
- ✅ Real-time data extraction
- ✅ Auto-sync functionality
- ✅ Risk analysis integration
- ✅ Notification system

### Roadmap
- 🔜 v1.1.0: Firefox extension support
- 🔜 v1.2.0: Offline mode with local caching
- 🔜 v1.3.0: Bulk operations (analyze all students)
- 🔜 v2.0.0: Direct integration (no API needed)

## 📄 License

MIT License - see LICENSE file in root directory

## 🤝 Support

- **Documentation**: [Agent Aura Wiki](https://github.com/05sumedh08/agent-aura/wiki)
- **Issues**: [GitHub Issues](https://github.com/05sumedh08/agent-aura/issues)
- **Email**: sumedhgurchal358@gmail.com
- **Author**: Sumedh Gurchal

## 🙏 Credits

Built with ❤️ by the Agent Aura Team

---

**Agent Aura Chrome Extension v1.0.0** - Bringing AI-powered student analytics to your fingertips
