# Welcome to WaniMoreKani
WaniMoreKani is a learning system for Japanese kanji. It acts as an extension to WaniKani, allowing you to solidify your Japanese vocabulary in new ways.

## What's the difference?

### WaniKani
WaniKani focuses on teaching the mapping of kanji to their english meaning. They combine the kanji in a coherent system so that you can identify groups of written kanji as vocabulary. In other words, you enhance your ability to read Japanese. 

```mermaid
graph LR
A((JP Kanji))------>B((ENG Vocabulary))
```

### WaniMoreKani
WaniMoreKani focuses on other mappings which help for speaking and comprehension. For instance, given a vocabulary word in your native language, are you able to find a matching word in Japanese?
```mermaid
graph LR
A((ENG Vocabulary))------>B((JP Kanji))

```

# Quickstart

## Requirements
- Python3
- WaniKani Account
- Japanese Keyboard Language Pack

## Installation
```
git clone https://github.com/DashKosaka/WaniMoreKani.git
cd WaniMoreKani
pip install -r requirements.txt
python manager.py initial-setup
*Follow the instructions in the command line*
```