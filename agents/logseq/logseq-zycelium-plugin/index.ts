import '@logseq/libs'
import { SettingSchemaDesc, SimpleCommandKeybinding } from '@logseq/libs/dist/LSPlugin';
import * as io from 'socket.io-client'


const settingsSchema: SettingSchemaDesc[] = [
  {
    key: "serverURL",
    type: "string",
    default: "https://localhost:3965",
    title: "Zycelium URL",
    description: "Visit the URL in your browser for advanced settings.",
  },
  {
    key: "agent_token",
    type: "string",
    default: "",
    title: "Agent Token",
    description: "Agent token used to authenticate with the Zycelium server.",
  },
]

async function settings_are_valid() {
  const server_url = logseq.settings!["serverURL"]
  const agent_token = logseq.settings!["agent_token"]
  if (!server_url) {
    console.error("Server URL not configured for Zycelium.")
    logseq.App.showMsg(
      "Please configure server URL for Zycelium.",
      "error"
    )
    return false
  }
  if (!agent_token) {
    console.error("Agent token not configured for Zycelium.")
    logseq.App.showMsg(
      "Please configure agent token for Zycelium.",
      "error"
    )
    return false
  }
  return true
}

async function main() {
  logseq.useSettingsSchema(settingsSchema)

  if (!await settings_are_valid()) {
    console.error("Zycelium settings are invalid, exiting.")
    return
  }

  const socket = io.connect(logseq.settings!["serverURL"], {
    reconnection: true,
    rejectUnauthorized: false,
    secure: true,
    transports: ['polling'],
  })

  socket.on('connect', async () => {
    console.log("Connected to Zycelium server.")
    socket.emit('logseq/ready')
    socket.emit('logseq/graph', await logseq.App.getCurrentGraph())
  })

  socket.onAny((event, ...args) => {
    console.log(event, args);
  });

  logseq.App.showMsg('Hello, World!')
}

logseq.ready(main).catch(console.error)
