# 📋 Simple Deployment Checklist Tool

A **clean, dark-themed** deployment tracking tool with minimal UI and maximum functionality.

## 🚀 Quick Start

```bash
# Launch the simplified version
pipenv shell
python simple_main.py
```

## 🎯 Features

### **Dark Theme UI**
- Dark background with white text
- Clean, minimal interface
- Easy on the eyes

### **Simple Deployment Workflow**
1. **Select Project** - Dropdown with all available projects
2. **Choose Components** - Checkboxes for Frontend/Backend/BackOffice
3. **View Project Info** - Auto-populated information box
4. **Enter Patch Number** - PAT-123 or JIRA-456 format
5. **Mark Build Success** - Single checkbox
6. **Save & Copy** - Instant Teams/JIRA format

### **Four Main Tabs**
- **Deployment** - Main workflow
- **Projects** - Add/Edit/Delete projects
- **History** - View past deployments
- **Settings** - Basic preferences

## 🖥️ UI Layout

```
┌─────────────────────────────────────────────┐
│ [Deployment] [Projects] [History] [Settings] │
├─────────────────────────────────────────────┤
│ Project: [MBANK          ▼]                │
│                                             │
│ Components: ☑Frontend ☑Backend ☐BackOffice │
│                                             │
│ ┌─ Project Information ─────────────────┐   │
│ │ • MBANK-FE: Frontend                  │   │
│ │   VCS: Git                            │   │
│ │   URL: https://github.com/...         │   │
│ │ • MBANK-BE: Backend                   │   │
│ │   Build: MVN                          │   │
│ └───────────────────────────────────────┘   │
│                                             │
│ Patch Number: [PAT-2024-001]               │
│                                             │
│ ☑ Build Successful                          │
│                                             │
│           [💾 Save Deployment]              │
│                                             │
│ Copy for Teams/JIRA:                       │
│ ┌───────────────────────────────────────┐   │
│ │ MBANK-FE,BE | PAT-2024-001 | ✅ Success │   │
│ │ Date: 2024-09-26 14:30               │   │
│ └───────────────────────────────────────┘   │
│           [📋 Copy to Clipboard]            │
└─────────────────────────────────────────────┘
```

## ⚡ Workflow

1. **Select project** → Components auto-enable
2. **Check components** → Choose Frontend/Backend/BackOffice
3. **Enter patch** → PAT-123 format
4. **Mark build success** → Single checkbox
5. **Save** → Updates database
6. **Copy text** → Paste in Teams/JIRA

## 📊 Copy Format Example

```
MBANK-FE,BE | PAT-2024-001 | ✅ Success
Date: 2024-09-26 14:30
Components: 2 deployed
```

## 🏗️ Project Management

- **Add projects** with Frontend/Backend/BackOffice components
- **Edit existing** project details
- **Delete projects** (with confirmation)
- **Auto-generate** component codes (PROJECT-FE, PROJECT-BE)

## 📈 History Tracking

- **View all deployments** in chronological order
- **Filter by project** or search patch IDs
- **Color-coded status** (Success = Green, Failed = Red)
- **Export to Excel** (coming soon)

## ⚙️ Settings

- **User name** for deployments
- **Default patch prefix** (PAT, JIRA, etc.)
- **Export path** for Excel files

## 🗂️ File Structure

```
chklst/
├── simple_main.py              # Launch simplified version
├── ui/
│   ├── dark_theme.py           # Dark theme stylesheet
│   ├── simple_deployment.py    # Main deployment workflow
│   ├── simple_projects.py      # Project management
│   ├── simple_history.py       # Deployment history
│   └── simple_settings.py      # Basic settings
├── database.py                 # Database models (shared)
└── README_SIMPLE.md           # This file
```

## 🎨 Design Philosophy

- **Simple over complex** - Clean, functional UI
- **Dark theme** - Easy on the eyes
- **Keyboard-friendly** - Tab navigation works
- **One-click workflow** - Minimal clicks to complete tasks
- **Copy-paste ready** - Instant sharing format

## 🔧 Comparison with Original

| Feature | Original | Simple |
|---------|----------|--------|
| Theme | Light, complex styling | Dark, minimal |
| Layout | Multiple group boxes | Clean sections |
| Components | Radio buttons | Checkboxes (multi-select) |
| Project Info | Multiple labels | Single text box |
| Copy Format | 3 format buttons | Single optimized format |
| UI Style | Fancy, colorful | Clean, professional |

## ✅ What Works

- **Project selection** with auto-population
- **Multi-component deployment** (Frontend + Backend)
- **Database integration** with existing data
- **Dark theme** throughout
- **Copy-paste functionality** for Teams/JIRA
- **Project CRUD operations**
- **Deployment history** with filtering

This simplified version focuses on **functionality over form**, providing exactly what you need without unnecessary complexity.