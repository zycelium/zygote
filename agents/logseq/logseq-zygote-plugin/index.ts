import '@logseq/libs'
import { BlockEntity, SettingSchemaDesc, SimpleCommandKeybinding } from '@logseq/libs/dist/LSPlugin';
import * as io from 'socket.io-client'

const settingsSchema: SettingSchemaDesc[] = [
  {
    key: "serverURL",
    type: "string",
    default: "https://localhost:3965",
    title: "Zygote URL",
    description: "Visit the URL in your browser for advanced settings.",
  },
  {
    key: "agent_token",
    type: "string",
    default: "",
    title: "Agent Token",
    description: "Agent token used to authenticate with the Zygote server.",
  },
]

async function settings_are_valid() {
  const server_url = logseq.settings!["serverURL"]
  const agent_token = logseq.settings!["agent_token"]
  if (!server_url) {
    console.error("Server URL not configured for Zygote.")
    logseq.App.showMsg(
      "Please configure server URL for Zygote.",
      "error"
    )
    return false
  }
  if (!agent_token) {
    console.error("Agent token not configured for Zygote.")
    logseq.App.showMsg(
      "Please configure agent token for Zygote.",
      "error"
    )
    return false
  }
  return true
}

async function getTodayJournal() {
  const d = new Date();
  const todayDateObj = {
    day: `${d.getDate()}`.padStart(2, "0"),
    month: `${d.getMonth() + 1}`.padStart(2, "0"),
    year: d.getFullYear(),
  };
  const todayDate = `${todayDateObj.year}${todayDateObj.month}${todayDateObj.day}`;

  let ret;
  try {
    ret = await logseq.DB.datascriptQuery(`
      [:find (pull ?p [*])
       :where
       [?b :block/page ?p]
       [?p :block/journal? true]
       [?p :block/journal-day ?d]
       [(= ?d ${todayDate})]]
    `);
  } catch (e) {
    console.error(e);
  }
  if (!ret) {
    console.error("Could not find today's journal page.")
    return null
  }
  return (ret[0][0] || {});
}

async function getTargetBlock(pageName: string, targetBlockName: string) {
  const pageBlocksTree = await logseq.Editor.getPageBlocksTree(pageName);
  let targetBlock;
  targetBlock = pageBlocksTree.find((block: { content: string }) => {
    return block.content === targetBlockName;
  });
  if (!targetBlock) {
    const newTargetBlock = await logseq.Editor.insertBlock(
      pageBlocksTree[0].uuid,
      targetBlockName,
      {
        before: pageBlocksTree[0].content ? false : true,
        sibling: true
      }
    );
    return newTargetBlock;
  }
  return targetBlock;
}

async function prefixTimestamp(text: string) {
  const d = new Date();
  const zero_padded_hours = `${d.getHours()}`.padStart(2, "0");
  const zero_padded_minutes = `${d.getMinutes()}`.padStart(2, "0");
  const timestamp = `${zero_padded_hours}:${zero_padded_minutes}`;
  return `${timestamp} - ${text}`;
}

async function main() {
  logseq.useSettingsSchema(settingsSchema)

  if (!await settings_are_valid()) {
    console.error("Zygote settings are invalid, exiting.")
    return
  }

  const socket = io.connect(logseq.settings!["serverURL"], {
    reconnection: true,
    rejectUnauthorized: false,
    secure: true,
    transports: ['websocket'],
    auth: {
      token: logseq.settings!["agent_token"],
    },
  })

  socket.on('connect', async () => {
    console.log("Connected to Zygote server.")
    socket.emit('logseq/ready', { "kind": "event", "name": "ready", "data": {} })
  })

  socket.on('event-telegram/message', async (frame) => {
    console.log("Received message from Telegram:", frame)

    if (frame.data.message.startsWith("/")) {
      console.log("Ignoring command:", frame.data.message)
      return
    }
    const message = await prefixTimestamp(frame.data.message)

    let todayJournalPage = await getTodayJournal()
    if (!todayJournalPage) {
      logseq.App.showMsg("Cannot find today's journal page.", "error")
      return
    }
    const targetBlock = await getTargetBlock(todayJournalPage.uuid, "[[Log]]")
    if (!targetBlock) {
      logseq.App.showMsg("Cannot find target block.", "error")
      return
    }
    await logseq.Editor.insertBlock(
      targetBlock.uuid,
      message,
      {
        before: false,
        sibling: false
      }
    )
  
  })

  socket.onAny((event, ...args) => {
    console.log(event, args);
  });

}

logseq.ready(main).catch(console.error)
