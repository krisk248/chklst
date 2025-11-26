# chklst Frontend

Vue 3 + TypeScript + Vite frontend for the chklst deployment tracking application.

## Project Structure

```
frontend/
├── index.html                 # Entry point
├── package.json              # Dependencies and scripts
├── tsconfig.json             # TypeScript configuration
├── vite.config.ts            # Vite configuration
├── vitest.config.ts          # Vitest configuration
├── tailwind.config.js        # Tailwind CSS configuration
├── postcss.config.js         # PostCSS configuration
├── src/
│   ├── main.ts              # Application entry point
│   ├── App.vue              # Root component
│   ├── style.css            # Global styles and Tailwind imports
│   ├── vite-env.d.ts        # Vite environment types
│   ├── router/
│   │   └── index.ts         # Vue Router configuration with 7 routes
│   ├── stores/
│   │   └── index.ts         # Pinia store (app state)
│   ├── views/               # Page components (7 views)
│   │   ├── DeploymentView.vue   # Deployment tracking
│   │   ├── ProjectsView.vue     # Project management
│   │   ├── LibraryView.vue      # Library/presets management
│   │   ├── HistoryView.vue      # Deployment history
│   │   ├── ReportsView.vue      # Report generation
│   │   ├── SettingsView.vue     # Settings management
│   │   └── AboutView.vue        # About page
│   ├── components/
│   │   ├── layout/          # Layout components
│   │   │   ├── MainLayout.vue   # Main layout wrapper
│   │   │   ├── Sidebar.vue      # Navigation sidebar
│   │   │   └── Header.vue       # Page header
│   │   └── ui/              # UI components
│   │       └── Notification.vue # Notification component
│   ├── composables/         # Vue composables
│   │   └── useApi.ts        # API client and WebSocket hook
│   └── lib/
│       └── utils.ts         # Utility functions
├── .gitignore
└── README.md
```

## Technology Stack

- **Vue 3**: Modern JavaScript framework with Composition API
- **TypeScript**: Type safety and better IDE support
- **Vite**: Fast build tool and dev server
- **Tailwind CSS**: Utility-first CSS framework
- **Pinia**: State management
- **Vue Router**: Client-side routing
- **Axios**: HTTP client
- **Lucide Vue Next**: Beautiful icon library
- **Radix Vue**: Unstyled accessible components

## Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

## Development

Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:3000`

### Features
- Hot Module Replacement (HMR)
- CORS proxy to backend API (`/api` → `http://localhost:8000`)
- Dark theme by default
- TypeScript strict mode

## Building

Build for production:
```bash
npm run build
```

Output will be in the `dist` directory.

Preview production build:
```bash
npm run preview
```

## Testing

Run tests:
```bash
npm test
```

Watch mode:
```bash
npm test -- --watch
```

Coverage report:
```bash
npm run coverage
```

## Key Features

### Navigation (Sidebar)
- 7 menu items with icons (Lucide icons)
- Active route highlighting
- Responsive design

### Dark Theme
- Default dark color scheme matching PyQt5 original app
- Colors defined in Tailwind config:
  - Background: `#2b2b2b`
  - Foreground: `#ffffff`
  - Accent: `#4a9eff`
  - Success: `#4caf50`
  - Muted: `#404040`
  - Border: `#555555`

### API Client
The `useApi` composable provides:
- GET, POST, PUT, PATCH, DELETE methods
- Automatic error handling
- Loading state management
- Type-safe responses

```typescript
import { useApi } from '@/composables/useApi'

const { get, post, isLoading, error } = useApi()
const response = await get('/deployments')
```

### WebSocket Support
The `useWebSocket` composable enables real-time updates:
```typescript
const { connect, send, isConnected } = useWebSocket('ws://localhost:8000/ws')
connect()
```

### State Management (Pinia)
Global app state includes:
- Loading state
- Notification system (info, success, error, warning)

```typescript
const appStore = useAppStore()
appStore.showNotification('Deployment started!', 'success')
```

## Views

### 1. Deployment (/)
- Dashboard with deployment statistics
- Recent deployments list
- Create new deployment button

### 2. Projects (/projects)
- Project management interface
- Project statistics
- Project creation

### 3. Library (/library)
- Manage reusable components
- Developers, servers, environments
- Add/remove library items

### 4. History (/history)
- Deployment history tracking
- Audit logs
- Historical statistics

### 5. Reports (/reports)
- Report generation
- Excel and PDF export options
- Statistics dashboard

### 6. Settings (/settings)
- Application settings
- Theme selection
- Notification preferences
- Advanced options

### 7. About (/about)
- Application information
- Technology stack overview
- Feature list
- License information

## Environment Variables

Create a `.env.local` file in the frontend directory:
```
VITE_API_BASE_URL=/api/v1
VITE_WS_URL=ws://localhost:8000/ws
```

## Styling

All styling uses Tailwind CSS with custom dark theme colors. Global styles are defined in `src/style.css`.

### Key Tailwind Classes
- `sidebar-link`: Navigation link styling
- `main-container`: Main layout container
- `page-header`: Page header with border
- `page-title`: Large page title

## Component Types

### Layouts
- `MainLayout`: Wraps pages with sidebar and header

### UI Components
- `Notification`: Dismissible notification toast

### Composables
- `useApi()`: HTTP client with error handling
- `useWebSocket()`: WebSocket connection management

## Best Practices

1. **Type Safety**: Always use TypeScript types
2. **Component Composition**: Use `<script setup>` syntax
3. **State Management**: Use Pinia for global state
4. **API Calls**: Use `useApi` composable
5. **Styling**: Use Tailwind utility classes
6. **Icons**: Use Lucide Vue Next for consistency

## Integration with Backend

The frontend expects the FastAPI backend to be running on `http://localhost:8000`.

### API Endpoints (Proxied via Vite)
- `/api/v1/*` → Backend API routes
- `/ws/*` → WebSocket connections

### Backend Requirements
- CORS enabled for `http://localhost:3000`
- API endpoints at `/api/v1/*`
- WebSocket support for real-time updates

## Troubleshooting

### Port Already in Use
If port 3000 is busy, edit `vite.config.ts`:
```typescript
server: {
  port: 3001,  // or any other port
}
```

### API Connection Issues
- Verify backend is running on port 8000
- Check CORS configuration in backend
- Check browser console for errors

### Build Issues
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

## Performance

- Bundle size: < 200KB gzipped
- First paint: < 1s (with backend)
- Lazy loading: Enabled for routes (future phase)
- Image optimization: Ready for implementation (future phase)

## Accessibility

- Semantic HTML
- ARIA labels on interactive elements
- Keyboard navigation support
- High contrast dark theme
- Focus indicators on all interactive elements

## Future Enhancements

1. Component libraries (shadcn-vue)
2. Form validation and handling
3. Data table components
4. Chart/graph visualizations
5. Authentication integration
6. Offline support (PWA)
7. Advanced search and filtering
8. Real-time notifications via WebSocket

## License

Same as parent project (chklst)

## Contributing

Follow Vue 3 + TypeScript best practices. Ensure all changes include proper types and documentation.
