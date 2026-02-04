module.exports = {
  apps: [
    // Option 1: Run individual watchers separately (recommended for production)
    {
      name: 'filesystem-watcher',
      script: 'python',
      args: 'run_watcher.py',
      interpreter: 'none',
      autorestart: true,
      watch: false,
      max_restarts: 10,
      min_uptime: '10s',
      error_file: 'logs/filesystem-watcher-error.log',
      out_file: 'logs/filesystem-watcher-out.log',
      env: {
        PYTHONUNBUFFERED: '1'
      }
    },
    {
      name: 'gmail-watcher',
      script: 'python',
      args: 'watchers/gmail_watcher.py',
      interpreter: 'none',
      autorestart: true,
      watch: false,
      max_restarts: 10,
      min_uptime: '10s',
      error_file: 'logs/gmail-watcher-error.log',
      out_file: 'logs/gmail-watcher-out.log',
      env: {
        PYTHONUNBUFFERED: '1'
      }
    },
    {
      name: 'whatsapp-watcher',
      script: 'python',
      args: 'watchers/whatsapp_watcher.py',
      interpreter: 'none',
      autorestart: true,
      watch: false,
      max_restarts: 10,
      min_uptime: '10s',
      error_file: 'logs/whatsapp-watcher-error.log',
      out_file: 'logs/whatsapp-watcher-out.log',
      env: {
        PYTHONUNBUFFERED: '1'
      }
    },
    {
      name: 'linkedin-watcher',
      script: 'python',
      args: 'watchers/linkedin_watcher.py',
      interpreter: 'none',
      autorestart: true,
      watch: false,
      max_restarts: 10,
      min_uptime: '10s',
      error_file: 'logs/linkedin-watcher-error.log',
      out_file: 'logs/linkedin-watcher-out.log',
      env: {
        PYTHONUNBUFFERED: '1'
      }
    },
    {
      name: 'orchestrator',
      script: 'python',
      args: 'orchestrator.py',
      interpreter: 'none',
      autorestart: true,
      watch: false,
      max_restarts: 10,
      min_uptime: '10s',
      error_file: 'logs/orchestrator-error.log',
      out_file: 'logs/orchestrator-out.log',
      env: {
        PYTHONUNBUFFERED: '1'
      }
    },

    // Option 2: Run all watchers via orchestrate_watchers.py (alternative approach)
    // Uncomment this and comment out individual watchers above to use this approach
    /*
    {
      name: 'multi-watcher-orchestrator',
      script: 'python',
      args: 'orchestrate_watchers.py',
      interpreter: 'none',
      autorestart: true,
      watch: false,
      max_restarts: 10,
      min_uptime: '10s',
      error_file: 'logs/multi-watcher-orchestrator-error.log',
      out_file: 'logs/multi-watcher-orchestrator-out.log',
      env: {
        PYTHONUNBUFFERED: '1'
      }
    },
    {
      name: 'orchestrator',
      script: 'python',
      args: 'orchestrator.py',
      interpreter: 'none',
      autorestart: true,
      watch: false,
      max_restarts: 10,
      min_uptime: '10s',
      error_file: 'logs/orchestrator-error.log',
      out_file: 'logs/orchestrator-out.log',
      env: {
        PYTHONUNBUFFERED: '1'
      }
    }
    */
  ]
};
