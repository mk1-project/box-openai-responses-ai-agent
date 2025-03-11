# box-openai-responses-ai-agent
The OpenAI Responses API will allow developers to inject additional data into the response. This includes web search, computer use, and other types of data. This repository shows how to use this new capability and a Box Agent to add proprietary unstructured data from your Box instance into your agentic work.

### Setup
Clone this repo:
```bash
git clone https://github.com/box-community/doc-gen-ai-workshop.git
```

Create a python virtual environment and activate it:
```bash
python3.13 -m venv .venv
source .venv/bin/activate
```

Install the requirements:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

You will also need to set up your environment. First you will need a Box Platform app using Client Credentials Grant for authorization. You will also need to install and enable that app in your admin console. 

Once that is done, create a file called `.env` at the root level of this project and add the following values:

```yaml
BOX_CLIENT_ID=your_box_client_id
BOX_CLIENT_SECRET=your_box_client_secret
BOX_SUBJECT_TYPE=user
BOX_SUBJECT_ID=your_box_user_id
```

You can also set `BOX_SUBJECT_TYPE` to enterprise and replace `your_box_user_id` with `your_box_enterprise_id`.

Finally, you will need to open a terminal window and in that shell, set your OpenAI API key to an environment variable with the following command:

```bash
export OPENAI_API_KEY=your_openai_api_key
```

Now in that terminal window, just run:

```bash
python main.py
```

The available tools you have at your disposal from Box in this example are:
* file_search - search all of Box for files
* ask_box - use the Box AI /ask endpoint
* get_text_from_file - get a text representation of your file
* box_search_folder_by_name - Find a folder by its name
* box_list_folder_content_by_folder_id - List all the files in a given folder