<template>
  <div class="space-y-6">
    <div class="page-header">
      <h1 class="page-title">About chklst</h1>
    </div>

    <div class="max-w-3xl">
      <Card>
        <!-- Application Header -->
        <div class="text-center mb-8 pb-8 border-b border-[#555555]">
          <h1 class="text-5xl font-bold text-[#4a9eff] mb-2">chklst</h1>
          <p class="text-xl text-gray-300">Deployment Tracking Tool</p>
          <p class="text-sm text-gray-500 mt-2">Version 2.0.0</p>
        </div>

        <!-- Description -->
        <div class="space-y-6">
          <div>
            <h2 class="text-2xl font-bold text-white mb-3">About This Application</h2>
            <p class="text-gray-300 leading-relaxed">
              chklst is a modern web application for tracking software deployments across multiple
              projects and environments. Originally developed as a PyQt5 desktop application, it has
              been transformed into a powerful and intuitive web interface built with Vue 3 and FastAPI.
            </p>
            <p class="text-gray-300 leading-relaxed mt-4">
              The application enables development and operations teams to efficiently manage deployment
              processes, track deployment history, generate comprehensive reports, and maintain centralized
              records of all deployments across various projects and environments.
            </p>
          </div>

          <!-- Key Features -->
          <div>
            <h2 class="text-2xl font-bold text-white mb-4">Key Features</h2>
            <div class="space-y-3">
              <div class="flex items-start gap-3">
                <div class="text-[#4a9eff] text-xl mt-1">✓</div>
                <div>
                  <p class="font-semibold text-white">Deployment Tracking</p>
                  <p class="text-gray-400 text-sm">Record and track all deployments with detailed information including JIRA IDs, timestamps, and status</p>
                </div>
              </div>
              <div class="flex items-start gap-3">
                <div class="text-[#4a9eff] text-xl mt-1">✓</div>
                <div>
                  <p class="font-semibold text-white">Project & Component Management</p>
                  <p class="text-gray-400 text-sm">Organize projects, manage multiple components per project, and maintain developer assignments</p>
                </div>
              </div>
              <div class="flex items-start gap-3">
                <div class="text-[#4a9eff] text-xl mt-1">✓</div>
                <div>
                  <p class="font-semibold text-white">JIRA & Teams Integration</p>
                  <p class="text-gray-400 text-sm">Quick copy-to-clipboard functionality formatted for JIRA and Microsoft Teams messaging</p>
                </div>
              </div>
              <div class="flex items-start gap-3">
                <div class="text-[#4a9eff] text-xl mt-1">✓</div>
                <div>
                  <p class="font-semibold text-white">Monthly Reports & Export</p>
                  <p class="text-gray-400 text-sm">Generate detailed deployment statistics and export data to Excel or PDF formats</p>
                </div>
              </div>
              <div class="flex items-start gap-3">
                <div class="text-[#4a9eff] text-xl mt-1">✓</div>
                <div>
                  <p class="font-semibold text-white">Library Management</p>
                  <p class="text-gray-400 text-sm">Maintain reusable presets for developers, build servers, deploy servers, and environments</p>
                </div>
              </div>
              <div class="flex items-start gap-3">
                <div class="text-[#4a9eff] text-xl mt-1">✓</div>
                <div>
                  <p class="font-semibold text-white">Real-time Updates</p>
                  <p class="text-gray-400 text-sm">WebSocket support for real-time updates across browser tabs and instances</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Technology Stack -->
          <div>
            <h2 class="text-2xl font-bold text-white mb-4">Technology Stack</h2>
            <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
              <div class="bg-[#404040] p-4 rounded-lg border border-[#555555]">
                <p class="font-semibold text-[#4a9eff] text-sm">Frontend</p>
                <p class="text-gray-300">Vue 3</p>
                <p class="text-gray-400 text-xs">TypeScript</p>
              </div>
              <div class="bg-[#404040] p-4 rounded-lg border border-[#555555]">
                <p class="font-semibold text-[#4a9eff] text-sm">Styling</p>
                <p class="text-gray-300">Tailwind CSS</p>
                <p class="text-gray-400 text-xs">Lucide Icons</p>
              </div>
              <div class="bg-[#404040] p-4 rounded-lg border border-[#555555]">
                <p class="font-semibold text-[#4a9eff] text-sm">State</p>
                <p class="text-gray-300">Pinia</p>
                <p class="text-gray-400 text-xs">Store Management</p>
              </div>
              <div class="bg-[#404040] p-4 rounded-lg border border-[#555555]">
                <p class="font-semibold text-[#4a9eff] text-sm">Backend</p>
                <p class="text-gray-300">FastAPI</p>
                <p class="text-gray-400 text-xs">Python</p>
              </div>
              <div class="bg-[#404040] p-4 rounded-lg border border-[#555555]">
                <p class="font-semibold text-[#4a9eff] text-sm">Database</p>
                <p class="text-gray-300">SQLAlchemy</p>
                <p class="text-gray-400 text-xs">SQLite/PostgreSQL</p>
              </div>
              <div class="bg-[#404040] p-4 rounded-lg border border-[#555555]">
                <p class="font-semibold text-[#4a9eff] text-sm">API</p>
                <p class="text-gray-300">REST</p>
                <p class="text-gray-400 text-xs">WebSocket</p>
              </div>
            </div>
          </div>

          <!-- Creator Info -->
          <div class="bg-[#404040] p-6 rounded-lg border border-[#555555]">
            <h2 class="text-2xl font-bold text-white mb-4">About the Developer</h2>
            <div class="space-y-2">
              <p class="text-gray-300">
                <span class="font-semibold">Developer:</span> Kannan
              </p>
              <p class="text-gray-300">
                <span class="font-semibold">Company:</span> TTS
              </p>
              <p class="text-gray-300 mt-4 leading-relaxed">
                This application was built with a focus on user experience, performance, and maintainability.
                The transition from desktop to web ensures accessibility across all platforms while maintaining
                the powerful functionality that teams depend on for deployment tracking and management.
              </p>
            </div>
          </div>

          <!-- License and Copyright -->
          <div class="text-center pt-8 border-t border-[#555555]">
            <p class="text-gray-300 mb-2">© 2025 chklst. All Rights Reserved.</p>
            <p class="text-gray-500 text-sm">Built with modern web technologies for optimal performance and user experience.</p>
          </div>
        </div>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import Card from '../components/ui/Card.vue'
</script>
