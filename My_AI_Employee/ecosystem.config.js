/**
 * PM2 Ecosystem Configuration for Silver Tier AI Employee
 *
 * Manages all watcher processes and orchestrator for 24/7 operation.
 * Provides automatic restart on failure, graceful shutdown, and health monitoring.
 *
 * Usage:
 *   pm2 start ecosystem.config.js           # Start all processes
 *   pm2 stop ecosystem.config.js            # Stop all processes
 *   pm2 restart ecosystem.config.js         # Restart all processes
 *   pm2 logs                                # View logs
 *   pm2 monit                               # Monitor processes
 *   pm2 startup                             # Configure system startup
 *   pm2 save                                # Save process list for reboot
 */

module.exports = {
  apps: [
    {
      name: 'gmail-watcher',
      script: 'uv',
      args: 'run python src/my_ai_employee/run_gmail_watcher.py',
      cwd: __dirname,
      interpreter: 'none',  // uv is already executable
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      max_restarts: 10,
      min_uptime: '10s',  // Process must run for 10s before considering it stable
      restart_delay: 5000,  // Wait 5s before restarting after crash
      watch: false,  // Don't restart on file changes
      env: {
        NODE_ENV: 'production',
      },
      error_file: './logs/gmail-watcher-error.log',
      out_file: './logs/gmail-watcher-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      kill_timeout: 5000,  // Wait 5s for graceful shutdown before SIGKILL
    },
    {
      name: 'whatsapp-watcher',
      script: 'uv',
      args: 'run python src/my_ai_employee/watchers/whatsapp_watcher.py',
      cwd: __dirname,
      interpreter: 'none',
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      max_restarts: 10,
      min_uptime: '10s',
      restart_delay: 5000,
      watch: false,
      env_file: '.env',  // Load environment variables from .env file
      env: {
        NODE_ENV: 'production',
      },
      error_file: './logs/whatsapp-watcher-error.log',
      out_file: './logs/whatsapp-watcher-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      kill_timeout: 5000,
    },
    // {
    //   name: 'linkedin-watcher',
    //   script: 'uv',
    //   args: 'run python src/my_ai_employee/watchers/linkedin_watcher.py',
    //   cwd: __dirname,
    //   interpreter: 'none',
    //   instances: 1,
    //   exec_mode: 'fork',
    //   autorestart: true,
    //   max_restarts: 10,
    //   min_uptime: '10s',
    //   restart_delay: 5000,
    //   watch: false,
    //   env: {
    //     NODE_ENV: 'production',
    //   },
    //   error_file: './logs/linkedin-watcher-error.log',
    //   out_file: './logs/linkedin-watcher-out.log',
    //   log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    //   merge_logs: true,
    //   kill_timeout: 5000,
    // },
    {
      name: 'filesystem-watcher',
      script: 'uv',
      args: 'run python src/my_ai_employee/watchers/filesystem_watcher.py',
      cwd: __dirname,
      interpreter: 'none',
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      max_restarts: 10,
      min_uptime: '10s',
      restart_delay: 5000,
      watch: false,
      env: {
        NODE_ENV: 'production',
      },
      error_file: './logs/filesystem-watcher-error.log',
      out_file: './logs/filesystem-watcher-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      kill_timeout: 5000,
    },
    {
      name: 'orchestrator',
      script: 'uv',
      args: 'run python src/my_ai_employee/orchestrator.py',
      cwd: __dirname,
      interpreter: 'none',
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      max_restarts: 10,
      min_uptime: '10s',
      restart_delay: 5000,
      watch: false,
      env: {
        NODE_ENV: 'production',
      },
      error_file: './logs/orchestrator-error.log',
      out_file: './logs/orchestrator-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      kill_timeout: 5000,
    },
    // =============================================================================
    // GOLD TIER: Social Media Watcher
    // =============================================================================
    {
      name: 'social-media-watcher',
      script: 'src/my_ai_employee/watchers/social_media_watcher.py',
      interpreter: 'python',
      cwd: __dirname,
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      max_restarts: 10,
      min_uptime: '10s',
      restart_delay: 5000,
      watch: false,
      env_file: '.env',  // Load environment variables from .env file
      env: {
        NODE_ENV: 'production',
        PYTHONUNBUFFERED: '1',
      },
      error_file: './logs/social-media-watcher-error.log',
      out_file: './logs/social-media-watcher-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      kill_timeout: 5000,
    },
  ],

  /**
   * Deployment configuration (optional)
   */
  deploy: {
    production: {
      user: 'node',
      host: 'localhost',
      ref: 'origin/main',
      repo: 'git@github.com:username/My_AI_Employee.git',
      path: '/var/www/production',
      'post-deploy': 'uv sync && pm2 reload ecosystem.config.js --env production && pm2 save',
    },
  },
};
