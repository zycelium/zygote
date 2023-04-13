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

The format of each event is not fixed yet.


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

### Using Zygote

In the WebUI

- Create a Space or two
- Create agents
- Have the agents join spaces
- Create a token for each agent
- Stop the server with Ctrl+C
- Run it again to load the built-in agents
- Configure agents that need API keys
- Restart server one more time 
- Watch your personal automation system so its thing

The above list of steps is merely a workaround for missing features
such auto-provisioning built-in agents and reloading agents upon
configuration changes. 
That is a work in progress.
