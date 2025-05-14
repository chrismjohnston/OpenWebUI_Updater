# OpenWebUI_Updater
A Python script to update OpenWebUI in Docker using Ollama

I used to dread opening Docker Desktop and seeing a notification that OpenWeb UI needed to be updated. 

First I would need to download the update. 
Then I needed to remember to delete the current container image before installing the update.
And the command to run was very long and I had to make sure I didn't forget to add the `--gpus all` flag.

I finally had it so I used Google Gemini 2.5 Pro to help me create a Python script to do it automatically. 

**Requirements**
- You must have Docker Desktop installed
- You must have Ollama installed\
- You need to be using Nvidia GPUs

**How to use**
Navigate to the folder where you downloaded the script
run the following command
```bash
python OpenWebUI_Update.py
```
you may need to enter `python3` depending on how you have Python configured on your machine. 

**Planned updates:**
When I have a moment I'd like to add a dialog when you run the script with the following questions
- Do you use NVIDIA GPUs? (Y/N)
- Do you use Ollama? (Y/N)

And based on these responses it selects the proper settings. 