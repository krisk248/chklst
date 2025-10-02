# 📋 chklst - Deployment Tracking & Checklist Tool

A **simple, Excel-based deployment tracking tool** designed to help teams manage and track their software deployments efficiently. Built with a clean dark-themed UI for comfortable daily use.

**Developed by:** Kannan
**Organization:** TTS

---

## 📖 What is chklst?

**chklst** is a desktop application that helps development and DevOps teams:
- **Track deployments** across multiple projects and environments
- **Maintain deployment history** in organized monthly Excel reports
- **Generate deployment summaries** for JIRA tickets and team notifications
- **Monitor deployment statistics** with built-in reports and analytics
- **Prevent duplicate deployments** with intelligent duplicate detection
- **Standardize deployment workflows** across teams

---

## 🎯 Key Features

### ✅ **Excel-Based Tracking**
- Automatic monthly Excel file generation per project
- Structured deployment logs with timestamps, JIRA IDs, and status
- History tracking for all deployment actions
- No database setup required - everything stored in Excel

### ✅ **Smart Duplicate Detection**
- Prevents duplicate deployments by JIRA ID matching
- Time-based proximity detection (5-minute window)
- Confirmation dialogs with duplicate details

### ✅ **Multi-Component Deployments**
- Track Frontend, Backend, and Backoffice components separately
- Support for multiple components in a single deployment
- Component-specific build and deployment servers

### ✅ **Project Management**
- Add, edit, and delete projects with ease
- Configure project-specific settings (VCS URLs, servers, databases)
- Copy existing projects as templates

### ✅ **Reports & Analytics**
- Monthly deployment statistics
- Success/failure rates for builds and deployments
- Component-wise deployment counts
- PDF report generation

### ✅ **Dark Theme UI**
- Easy on the eyes for long working hours
- Clean, professional interface
- Keyboard-friendly navigation

---

## 🖥️ Screenshots

### Main Deployment Screen
*[Screenshot 1 will be added here]*

### Project Management
*[Screenshot 2 will be added here]*

### Deployment Reports
*[Screenshot 3 will be added here]*

### Settings & Configuration
*[Screenshot 4 will be added here]*

---

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pipenv (for dependency management)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd chklst
   ```

2. **Install dependencies**
   ```bash
   pipenv install
   ```

3. **Activate virtual environment**
   ```bash
   pipenv shell
   ```

4. **Run the application**
   ```bash
   python main_new.py
   ```

---

## 🚀 Quick Start Guide

### 1. **Add a Project**
   - Go to the **Projects** tab
   - Click "Add New Project"
   - Fill in project details (name, components, servers, VCS URLs)
   - Save the project

### 2. **Record a Deployment**
   - Go to the **Deployment** tab
   - Select your project from the dropdown
   - Choose components (Frontend/Backend/Backoffice)
   - Enter JIRA Patch ID (e.g., PROJ-123)
   - Fill in deployment details (timestamp, servers, database info)
   - Mark build and deployment status
   - Click "Save Deployment"

### 3. **View Reports**
   - Go to the **Reports** tab
   - Select month and year
   - View deployment statistics and charts
   - Generate PDF reports if needed

### 4. **Check Deployment History**
   - Go to the **Last Saved** tab
   - View recent deployments across all projects
   - Filter by project or date

---

## 📂 File Structure

```
chklst/
├── main_new.py                    # Main application entry point
├── ui/                            # UI components
│   ├── simple_deployment_new.py   # Deployment form
│   ├── simple_projects_form.py    # Project management
│   ├── simple_reports.py          # Reports viewer
│   ├── simple_last_saved.py       # Recent deployments
│   ├── simple_settings.py         # Settings
│   └── dark_theme.py              # Dark theme styling
├── utils/                         # Utility modules
│   ├── excel_manager.py           # Excel operations
│   └── pdf_generator.py           # PDF report generation
├── projects/                      # Project JSON files (gitignored)
├── reports/                       # Monthly Excel reports (gitignored)
├── settings.json                  # User settings
└── README.md                      # This file
```

---

## 🛠️ How It Works

### Deployment Workflow

1. **User selects a project** → Project configuration loads automatically
2. **User selects components** → Frontend/Backend/Backoffice checkboxes
3. **User enters deployment details** → JIRA ID, servers, timestamps, etc.
4. **System checks for duplicates** → Prevents accidental re-submissions
5. **User confirms and saves** → Data written to monthly Excel file
6. **History logged** → All actions tracked in History sheet

### Data Storage

- **Project Configurations**: Stored as JSON files in `projects/` folder
- **Deployment Records**: Stored in Excel files organized by month (`reports/MMM_YYYY/ProjectName.xlsx`)
- **Each Excel file contains**:
  - **Deployments Sheet**: Main deployment records
  - **History Sheet**: Audit log of all actions

### Monthly Organization

Reports are automatically organized into monthly folders:
```
reports/
├── Oct_2025/
│   ├── ProjectA.xlsx
│   ├── ProjectB.xlsx
│   └── ProjectC.xlsx
└── Nov_2025/
    ├── ProjectA.xlsx
    └── ProjectB.xlsx
```

---

## 📊 Excel Report Format

### Deployments Sheet Columns:
- JIRA PATCH ID
- Timestamp (DD-MMM-YYYY HH:MMAM/PM)
- Project Name
- Component Name
- Environment (QA/Staging/Production)
- SVN/GIT URL
- Developer Name
- Build Server
- Deploy Server
- Database Name
- Database Script
- Backup Location
- Build Status (Success/Failed)
- Deploy Status (Success/Failed)
- Notes
- Deployed By

### History Sheet Columns:
- Timestamp
- Action (Deployment Saved, Duplicate Detected, etc.)
- Project
- Component
- JIRA ID
- User
- Details
- Status (Success/Warning/Error)

---

## ⚙️ Configuration

### Settings (via Settings Tab)
- **User Name**: Default name for "Deployed By" field
- **Default Environment**: QA, Staging, or Production
- **Auto-copy Format**: Automatically copy deployment summary after save

### Project Settings (per project)
- Component-specific VCS URLs
- Build servers
- Deploy servers
- Database configurations
- Backup locations

---

## 🎨 Design Philosophy

- **Simplicity First**: Clean, uncluttered interface
- **Excel-Based**: No complex databases - familiar Excel format
- **Dark Theme**: Comfortable for extended use
- **Duplicate Prevention**: Smart checks to avoid mistakes
- **Audit Trail**: Complete history of all actions
- **Monthly Reports**: Organized, easy-to-find deployment records

---

## 🤝 Contributing

This is an internal TTS tool. For questions or issues, please contact the development team.

---

## 📝 License

Internal use only - TTS Organization

---

## 👤 Developer

**Kannan**
TTS Organization

---

## 🔄 Version History

- **v1.0** - Initial release with Excel-based tracking
- Deployment form with duplicate detection
- Project management
- Monthly Excel reports
- Dark theme UI

---

## 📧 Support

For support or feature requests, please contact the TTS development team.
