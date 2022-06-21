
# Installing ES

for this repo to work locally, Elasticsearch and Kibana should be installed.
For macos the homebrew library has these included so install is simpler...

# Installing python dependencies

To setup the python env, the code is tested with miniconda,
but any py3.8+ install with the **requirements.txt** package list should be enough.
The code uses tensorflow, but no gpu is required, because the repo used a pre-trained model

To run the repo the tf universal sentence encoder has to be downloaded and configured in the proper location.
The model is located here 
https://tfhub.dev/google/universal-sentence-encoder/2?tf-hub-format=compressed

once the model is downloaded and unzipped, the model path should be updated in **src/config.py**
in the variable **model_path** ...

# Indexing the aws docs paragraphs

In order to index the crawled json files, the script **src/main.py** can be started,
in the format `
python src/main.py jsons_path
`
Then a new index is created, the paragraphs are indexed, 
with a 512 feature vector included,
which is trained on the headings and text of each paragraph.

# Running the query

The main script of the repo is located in **src/main_query.py**
The query strings are located in **src/config.py**.
After each paragraph is indexed, the query can be run.

`
python src/main_query.py
`

This script should produce a html file inside **data/aws** with the crawled and sorted paragraphs.

# Crawling the docs

The docs where crawled using a jupyter lab notebook, located inside **workspace/**.
The json crawled files are currently located also in the **workspace/** folder.


# The frontend output

the output now is stored inside **data/aws** folder. 

the file is called scrolled_conts.html,
to use the file some css files are needed, not inline,
they are in the same folder.