# zygote

Zygote: Personal Automation Framework


## What is Zycelium Zygote?

The Zycelium Project aims to build a connect-everything network 
made by and for privacy-minded, security-aware, python-literate
individuals.

Zygote is an automation system to create and run personal agents.

Agents are code that interfaces with the world outside Zygote 
and provides APIs that the owner of an instance can use to 
automate pretty much anything as long as there's an agent for it.

Zygote does not restrict itself to IoT or home automation,
you can automate online APIs, apps running on your machines,
create a chatbot for yourself, scrape the web, 
ssh into your machines and perform tasks… you get the idea,
all you need is (someone/you) to write Python code to make it so.

## How far along is the project?

As of now, it is in the prototyping stage.

I am exploring various Python libraries to write code that is 
easy to read and understand in a weekend or two.
I find this part necessary to trust the framework that will
have a complete view of my entire life.

As of now, writing agents that pull information from APIs
and post to other APIs is possible.
Another agent can patch the events coming from one agent 
to another.

The format of each frame is not fixed yet.
And at the moment only events are available.
More kinds of frames will be added later.

---

## Okay, but what is this thing, really?

A Zygote instance provides you with a few building blocks / concepts 
that you can use to design automation for your needs.

### Entity

An entity is any web API, locally running app or 
hardware that you can program. 
An entity could be your desk-lamp, with one or more Components
such as the power switch, a dial for brightness, and the LED itself.
Another entity could be your indoor plant with sensors to detect
the humidity and temperature of soil, perhaps another sensor
to detect duration and intensity of received sunlight.

And of course, you yourself are an entity within the system,
with one or more interfaces available to you - via a web app,
a chat interface, perhaps some day a dedicated mobile app, 
any sensors you choose to use.

But how does Zygote 'talk' to all these various entities?

### Agent

Think of an agent as a high-level "driver" for any Entity 
in the physical or software realm.
The agent translates back and forth between the entity 
and your Zygote instance.
The agent can also be programmed to perform certain actions
on its on based on the state of the entity.

Little details such as don't turn the air-conditioning 
(or another heavy electrical device) on and off rapidly
can be built into the agent, so that even if the logic
in Zygote fails to account for this small but important
detail, the agent will ensure the entity is not damaged.

There is no "AI" involved here for obvious reasons - 
most important being that one can not reason about
a black box that you are expected to trust blindly.

An agent is programmed to do the bare minimum autonomous function
to ensure the entity it is responsible for is not harmed by accident.

A more mundane function would be to respect rate-limiting of external APIs.

Agents can respond to (or send) events, messages, requests or commands,
collectively called frames.

### Frame

A frame in Zygote is a packet of information (JSON object) 
that is send back and forth between an agent and the instance. 
Depending on instance owner's configuration, 
the frame may be broadcast to other agents.

A frame may be one of the following kinds:

- Event
- Message
- Request/response
- Command

#### Event

An event is sent by the instance to an agent or from an agent to the instance 
(and possibly broadcast to other agents) to notify about a change or it could
be a regular update based on time.

Imagine temperature measurement from a sensor that's sent out every minute.
The measurement may or may not change, but the time has changed and hence
an event is sent.
A door opening or closing is another event and is sent immediately by the sensor,
time does not matter here.
A new track playing on your music app is another event.
Pressing a hardware button is an event too.

Events are sent off and that's the end of responsibility for the agent.
An event may be used by another agent or it may be ignored.
An agent does not have access to past events.


#### Message

Messages in Zygote are meant to send text messages like we send each other.
However, on a single-user, personal instance, the messages may be used by 
agents that can parse the text and perform actions based on them.

Notifications from any agent that should be read by a person are send as messages.

Messages sent to an agent (including you) are held 
in the agent's inbox until acknowledged/read or deleted.
Messages may be broadcast, just like events - thus multiple agents 
will have the same message in their inbox.
Once acknowledged or deleted, the messages are removed from the inbox.


#### Request (and response)

Requests expect a response or may time-out if a response 
is not received within given time.

This allows building automations where it is necessary to acknowledge 
and act on the request or throw an error within certain time if the 
expected action is not taken.

Requests are generally sent to one agent at a time, however, it is possible to
have multiple agents that respond to the same request and the agent that initiated
the request can choose between waiting for 1 or more responses, with a timeout.

Requests are similar to messages - they can be marked 
to be held in the receiving agent's inbox until acknowledged or deleted.
This feature is useful if you would like automations that remind you to 
perform certain tasks, and once you respond, the automation continues.

#### Command

Commands are sent from the instance to an agent or from an agent to an instance.
Commands are never broadcast to other agents.

Commands are used to configure an agent, update its state in the database
so it can continue where it left off even after a restart.

Agents can be commanded to restart, update, change WiFi passwords etc.

Commands are not stored in the inbox and are expected 
to be executed immediately if the agent is online.
Commands are acknowledged, like requests but are not held in the inbox.


### Spaces

Agents do not have the ability to directly address other agents.
The instance owner decides which agents may receive frames sent by other agents.
To interact with other agents, the agents must join a space.

A space is similar to a chat room - many agents may join a space,
and an agent may join multiple spaces.

This gives a simple yet granular control over 
what information is available to which agents.
Any agents you don't fully trust - a program you just downloaded,
can be restricted to interaction with just one more agent
to do its job.
For example, it does not need to have visibility 
of other agents that send events about where you are or what you are doing.

---

And that's about it, now you know all the concepts necessary to start using Zygote
and build your own personal automation system as you like, on your terms.


## I want to try it out!

Be warned that this is very much a work in progress
and things break all the time.
If you are okay with that, welcome aboard!


### Install

```
git clone https://github.com/zycelium/zygote.git
cd zygote
poetry install
poetry run zygote serve
```

If you don't have `poetry` installed, get it with `python3 -m pip install poetry`

Once running, you can access the WebUI at https://localhost:3965/


Zygote has a few built-in agents and some that you can install as you need.
Built in and installed agents are provisioned in the database automatically.
To install extra agents, find them in the `agents` directory in the project root.

Example:

```
poetry shell
cd agents/openweather
pip install -e .
```

### Using Zygote


In the WebUI

- Create a Space named "home"
- Go to the Agents page to see all available agents
- Click on each agent name to open Agent page
  - Join "home" space
  - In the Update section, configure agents if they require API keys.
- Stop the server with Ctrl+C
- Run it again
- Watch your personal automation system do its thing

The above list of steps is merely a workaround for missing features
such as reloading agents upon configuration changes. 
Please note, this is a work in progress.


## Credits:

The project uses top 10,000 words from contemporary English to limit the vocabulary,
in hope that the project will be easy to approach for non-native English speakers.

The word-list is placed in the project directory as "dictionary.txt"

Source:
- https://github.com/first20hours/google-10000-english/
- https://github.com/first20hours/google-10000-english/blob/master/google-10000-english-no-swears.txt
