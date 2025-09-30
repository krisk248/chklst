# 📋 chklst - Excel-Based Deployment Tracker

## 🚀 New Excel-Based Architecture

This is the **new and improved** version of the deployment tracking system that uses **Excel files** for deployment history instead of SQLite database. This eliminates all the previous object/string attribute errors and provides a simpler, more portable solution.

## ✨ Key Features

### 📊 **Monthly Excel Reports**
- Each project gets its own Excel file per month: `reports/Month_Year/Project.xlsx`
- 16 columns with all deployment details
- Auto-formatted with success/failure color coding
- Built-in filters and sorting

### 🔧 **Simple UI with Auto-Fill**
- Minimal user input required (only 6 fields)
- Auto-fills from JSON project configuration
- Enhanced time picker with NOW button and calendar
- Status checkboxes for easy input

### 📈 **PDF Report Generation**
- Monthly summary reports with charts
- Success rate analysis
- Project performance metrics
- Deployment frequency trends

### 📁 **File-Based Architecture**
- **No database** - completely file-based
- JSON files for project configuration
- Excel files for deployment history
- Easy backup and sharing

## 🗂️ File Structure

```
chklst/
├── main_new.py                    # New main application
├── projects/                      # Project configurations (JSON)
│   ├── ADIB_MIG.json
│   ├── MBANK.json
│   └── ...
├── reports/                       # Monthly deployment records
│   ├── Dec_2024/
│   │   ├── ADIB_MIG.xlsx
│   │   ├── MBANK.xlsx
│   │   └── ...
│   └── pdfs/                      # Generated PDF reports
│       ├── December_2024_deployment_report.pdf
│       └── ...
├── utils/
│   ├── excel_manager.py           # Excel operations
│   ├── json_manager.py            # JSON project management
│   └── pdf_generator.py           # PDF report generation
└── ui/
    ├── simple_deployment_new.py   # New deployment form
    ├── simple_reports.py          # Reports viewer
    └── ...
```

## 🔧 Installation & Setup

### Prerequisites
```bash
# Python 3.8+ with pipenv
pipenv install
```

### Dependencies
- **PyQt5** - GUI framework
- **openpyxl** - Excel file handling
- **reportlab** - PDF generation
- **matplotlib** - Charts and graphs

## 🚀 Running the Application

### Quick Start
```bash
pipenv run python main_new.py
```

### Test the System
```bash
pipenv run python test_excel_flow.py
```

## 📋 Usage Guide

### 1. **Project Configuration**
- Use the **Projects** tab to manage project settings
- Each project has:
  - Environment (default: QA)
  - Build/Deploy servers
  - Database details
  - Backup location
  - Component configurations

### 2. **Recording Deployments**
- Use the **Deployment** tab
- Select project and component
- Auto-filled fields: Environment, Developer, Servers, etc.
- User input: JIRA ID, Timestamp, DB Script, Status, Notes, Deployed By

### 3. **Viewing Reports**
- Use the **Reports** tab
- Select month/year
- View summary, deployments table, and statistics
- Export to Excel or generate PDF reports

## 📊 Excel File Format

Each monthly Excel file contains 16 columns:

| Column | Description | Source |
|--------|-------------|---------|
| JIRA PATCH ID | Ticket number | User input |
| Timestamp | Date and time | User selectable |
| Project Name | Project identifier | Auto-filled |
| Component Name | Frontend/Backend/Backoffice | Auto-filled |
| Environment | Deployment environment | Auto-filled (QA) |
| SVN/GIT URL | Version control URL | Auto-filled |
| Developer Name | Component developer | Auto-filled |
| Build Server | Build server address | Auto-filled |
| Deploy Server | Deployment server | Auto-filled |
| Database Name | Database identifier | Auto-filled |
| Database Script | DB script name | User input |
| Backup Location | Backup path | Auto-filled |
| Build Status | Success/Failed | User checkbox |
| Deploy Status | Success/Failed | User checkbox |
| Notes | Deployment notes | User input |
| Deployed By | User name | User input |

## 📈 PDF Reports Include

### Executive Summary
- Total deployments
- Success rates
- Active projects
- Key insights

### Charts & Analytics
- Success rate pie charts
- Project deployment bar charts
- Component breakdown
- Trend analysis

### Detailed Statistics
- Project performance
- Developer productivity
- Component analysis
- Monthly comparisons

## 🔄 Data Flow

```
JSON Config → UI Auto-fill → User Input → Excel Storage → Reports & PDF
```

1. **Configuration**: Project details stored in JSON files
2. **Auto-fill**: UI populates from JSON configuration
3. **User Input**: Minimal fields for deployment details
4. **Storage**: Direct save to monthly Excel files
5. **Reporting**: Read from Excel for viewing and PDF generation

## ✅ Benefits of Excel-Based Approach

### 🎯 **Simplicity**
- No database setup or maintenance
- Files can be opened directly in Excel
- Easy to understand and modify

### 🚀 **Performance**
- Fast file operations
- No database locks or constraints
- Instant backup by copying files

### 🔧 **Portability**
- Self-contained project folders
- Easy to share project history
- Works without database server

### 🛡️ **Reliability**
- No attribute access errors
- Simple dictionary-based data flow
- Clear separation of concerns

## 🧪 Testing

Run the comprehensive test suite:

```bash
pipenv run python test_excel_flow.py
```

Tests verify:
- ✅ Directory structure creation
- ✅ JSON project management
- ✅ Excel deployment tracking
- ✅ PDF report generation

## 🔧 Maintenance

### Backup Strategy
- Copy entire `chklst` folder for complete backup
- Individual project backup: copy project JSON + monthly Excel files
- PDF reports: automatically archived in `reports/pdfs/`

### File Management
- Monthly Excel files: `reports/Month_Year/Project.xlsx`
- Automatic folder creation by month/year
- Old files can be archived by moving folders

## 🆚 Comparison with Previous Version

| Feature | Old (Database) | New (Excel) |
|---------|----------------|-------------|
| Storage | SQLite database | Excel + JSON files |
| Complexity | High (ORM, migrations) | Low (file operations) |
| Portability | Database dependent | Fully portable |
| User Access | App only | Excel + App |
| Backup | Database export | File copy |
| Errors | Attribute access issues | None |
| Maintenance | Schema migrations | File management |

## 🎯 Next Steps

1. **Run the application**: `pipenv run python main_new.py`
2. **Configure projects** in the Projects tab
3. **Record deployments** in the Deployment tab
4. **Generate reports** in the Reports tab
5. **Share Excel files** directly with stakeholders

---

## 🏁 **Ready to Use!**

The Excel-based deployment tracker is **fully functional** and **error-free**. It provides a simple, efficient, and reliable solution for tracking deployment activities with beautiful reports and easy data access.

**Happy tracking! 📊✨**