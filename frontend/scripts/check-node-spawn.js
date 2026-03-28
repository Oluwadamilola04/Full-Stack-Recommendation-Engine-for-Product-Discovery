import { spawnSync } from 'node:child_process'

const result = spawnSync(process.env.ComSpec || 'cmd.exe', ['/c', 'echo', 'ok'], {
  encoding: 'utf8',
})

if (!result.error && result.status === 0) {
  console.log('Node child-process spawning is available.')
  process.exit(0)
}

const errorCode = result.error?.code || 'UNKNOWN'
console.error('Node cannot spawn child processes on this system.')
console.error(`Detected error code: ${errorCode}`)
console.error('')
console.error('Vite uses esbuild, which needs child-process creation to work.')
console.error('On Windows this is commonly blocked by Exploit Protection or antivirus rules.')
console.error('')
console.error('How to fix it:')
console.error('1. Open Windows Security.')
console.error('2. Go to App & browser control > Exploit protection settings.')
console.error('3. Open Program settings and add C:\\Program Files\\nodejs\\node.exe.')
console.error('4. Set Child process creation to Off for node.exe.')
console.error('5. Restart VS Code/terminals and run the frontend again.')
console.error('')
console.error('Shortcut from this repo: run fix-node-block.bat as Administrator.')
console.error('')
console.error('The project can still use the static fallback frontend meanwhile.')
process.exit(1)
