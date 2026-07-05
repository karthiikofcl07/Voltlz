import { spawn } from 'node:child_process';

const commands = [
  ['python', ['-m', 'uvicorn', 'backend.app.main:app', '--host', '0.0.0.0', '--port', '8000']],
  ['npx', ['vite', '--host', '0.0.0.0', '--port', '3000']]
];

const children = commands.map(([cmd, args]) => {
  const child = spawn(cmd, args, { stdio: 'inherit', shell: false });
  child.on('exit', code => {
    if (code !== 0) process.exitCode = code;
  });
  return child;
});

process.on('SIGINT', () => {
  children.forEach(child => child.kill('SIGINT'));
});
